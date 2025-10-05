"""
Pipeline de enriquecimento de artigos científicos PMC.

Este módulo implementa um sistema completo para:
1. Buscar metadados via NCBI E-utilities
2. Obter texto completo via OAI-PMH
3. Extrair informações estruturadas com NLP/LLM
4. Salvar em banco de dados MongoDB/PostgreSQL
"""

import asyncio
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json

import aiohttp
import google.generativeai as genai
from pymongo import MongoClient


@dataclass
class ArticleMetadata:
    """Estrutura de dados para metadados de artigo."""
    experiment_id: str
    doi: Optional[str] = None
    title: Optional[str] = None
    abstract: Optional[str] = None
    summary_en: Optional[str] = None  # Resumo em inglês
    year: Optional[int] = None
    authors: List[str] = None
    institutions: List[str] = None
    funding: List[str] = None
    objectives: List[str] = None
    hypotheses: List[str] = None
    organisms: List[str] = None
    conditions: List[str] = None
    methods: List[str] = None
    parameters_measured: List[str] = None
    results_summary: Optional[str] = None
    significant_findings: List[str] = None
    implications: List[str] = None
    limitations: List[str] = None
    future_directions: List[str] = None
    duration: Optional[str] = None
    sample_size: Optional[int] = None
    conditions_control: List[str] = None
    related_projects: List[str] = None
    citations: Optional[int] = None
    full_text: Optional[str] = None
    mesh_terms: List[str] = None
    journal: Optional[str] = None
    pmid: Optional[str] = None
    
    def __post_init__(self):
        """Inicializa listas vazias se None."""
        if self.authors is None:
            self.authors = []
        if self.institutions is None:
            self.institutions = []
        if self.funding is None:
            self.funding = []
        if self.objectives is None:
            self.objectives = []
        if self.hypotheses is None:
            self.hypotheses = []
        if self.organisms is None:
            self.organisms = []
        if self.conditions is None:
            self.conditions = []
        if self.methods is None:
            self.methods = []
        if self.parameters_measured is None:
            self.parameters_measured = []
        if self.significant_findings is None:
            self.significant_findings = []
        if self.implications is None:
            self.implications = []
        if self.limitations is None:
            self.limitations = []
        if self.future_directions is None:
            self.future_directions = []
        if self.conditions_control is None:
            self.conditions_control = []
        if self.related_projects is None:
            self.related_projects = []
        if self.mesh_terms is None:
            self.mesh_terms = []


class NCBIAPIClient:
    """Cliente para APIs da NCBI."""
    
    BASE_ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    BASE_EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    BASE_OAI = "https://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi"
    
    def __init__(self, email: str = "your_email@example.com"):
        """
        Inicializa cliente NCBI.
        
        Args:
            email: Email para identificação (boas práticas NCBI)
        """
        self.email = email
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.session:
            await self.session.close()
    
    @staticmethod
    def extract_pmcid(url_or_id: str) -> str:
        """
        Extrai PMCID de URL ou string.
        
        Args:
            url_or_id: URL PMC ou PMCID
            
        Returns:
            PMCID sem prefixo 'PMC'
            
        Examples:
            'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2998437/' -> '2998437'
            'PMC2998437' -> '2998437'
        """
        match = re.search(r'PMC(\d+)', url_or_id)
        if match:
            return match.group(1)
        # Se já for apenas números
        if url_or_id.isdigit():
            return url_or_id
        raise ValueError(f"Não foi possível extrair PMCID de: {url_or_id}")
    
    async def fetch_metadata(self, pmcid: str) -> Dict[str, Any]:
        """
        Busca metadados via ESummary API.
        
        Args:
            pmcid: ID do PMC (sem prefixo PMC)
            
        Returns:
            Dicionário com metadados
        """
        params = {
            'db': 'pmc',
            'id': pmcid,
            'retmode': 'json',
            'email': self.email
        }
        
        async with self.session.get(self.BASE_ESUMMARY, params=params) as response:
            if response.status != 200:
                print(f"[ERRO] ESummary falhou para PMC{pmcid}: {response.status}")
                return {}
            
            data = await response.json()
            
            # Navegar na estrutura JSON da resposta
            if 'result' in data and pmcid in data['result']:
                return data['result'][pmcid]
            
            return {}
    
    async def fetch_fulltext_xml(self, pmcid: str) -> Optional[str]:
        """
        Busca texto completo via OAI-PMH em formato JATS XML.
        
        Args:
            pmcid: ID do PMC (sem prefixo PMC)
            
        Returns:
            XML string ou None se não disponível
        """
        params = {
            'verb': 'GetRecord',
            'identifier': f'oai:pubmedcentral.nih.gov:{pmcid}',
            'metadataPrefix': 'pmc'
        }
        
        async with self.session.get(self.BASE_OAI, params=params) as response:
            if response.status != 200:
                print(f"[AVISO] OAI-PMH falhou para PMC{pmcid}: {response.status}")
                return None
            
            xml_content = await response.text()
            
            # Verificar se há erro no XML
            if 'error' in xml_content.lower() or 'norecordsmatch' in xml_content.lower():
                return None
            
            return xml_content
    
    async def fetch_front_matter(self, pmcid: str) -> Optional[str]:
        """
        Busca front matter (metadados de autores/afiliações) via OAI-PMH.
        
        Args:
            pmcid: ID do PMC (sem prefixo PMC)
            
        Returns:
            XML string com front matter ou None se não disponível
        """
        params = {
            'verb': 'GetRecord',
            'identifier': f'oai:pubmedcentral.nih.gov:{pmcid}',
            'metadataPrefix': 'pmc_fm'  # Front Matter
        }
        
        async with self.session.get(self.BASE_OAI, params=params) as response:
            if response.status != 200:
                print(f"[AVISO] OAI-PMH front matter falhou para PMC{pmcid}: {response.status}")
                return None
            
            xml_content = await response.text()
            
            # Verificar se há erro no XML
            if 'error' in xml_content.lower() or 'norecordsmatch' in xml_content.lower():
                return None
            
            return xml_content
    
    async def fetch_pubmed_details(self, pmid: str) -> Dict[str, Any]:
        """
        Busca detalhes adicionais via PubMed EFetch.
        
        Args:
            pmid: PubMed ID
            
        Returns:
            Dicionário com dados do PubMed
        """
        params = {
            'db': 'pubmed',
            'id': pmid,
            'retmode': 'xml',
            'email': self.email
        }
        
        async with self.session.get(self.BASE_EFETCH, params=params) as response:
            if response.status != 200:
                return {}
            
            xml_content = await response.text()
            return self._parse_pubmed_xml(xml_content)
    
    @staticmethod
    def _parse_pubmed_xml(xml_content: str) -> Dict[str, Any]:
        """Parse XML do PubMed para extrair metadados."""
        try:
            root = ET.fromstring(xml_content)
            data = {}
            
            # MeSH terms
            mesh_terms = []
            for mesh in root.findall('.//MeshHeading/DescriptorName'):
                mesh_terms.append(mesh.text)
            data['mesh_terms'] = mesh_terms
            
            # Funding
            funding = []
            for grant in root.findall('.//Grant'):
                agency = grant.find('Agency')
                grant_id = grant.find('GrantID')
                if agency is not None:
                    grant_text = agency.text
                    if grant_id is not None:
                        grant_text += f" {grant_id.text}"
                    funding.append(grant_text)
            data['funding'] = funding
            
            return data
            
        except ET.ParseError:
            return {}


class JAATSParser:
    """Parser para XML JATS (Journal Article Tag Suite)."""
    
    @staticmethod
    def parse_front_matter(xml_content: str) -> Dict[str, Any]:
        """
        Parse front matter XML para extrair autores e afiliações.
        
        Args:
            xml_content: XML string do front matter
            
        Returns:
            Dicionário com authors e institutions
        """
        try:
            root = ET.fromstring(xml_content)
            
            # Extrair do envelope OAI se necessário
            if 'OAI-PMH' in root.tag or 'oai' in root.tag.lower():
                # Buscar o front ou article-meta
                front_elem = root.find('.//front')
                if front_elem is not None:
                    root = front_elem
                else:
                    # Tentar achar article-meta
                    article_meta = root.find('.//article-meta')
                    if article_meta is not None:
                        root = article_meta
            
            data = {'authors': [], 'institutions': set()}
            
            # Buscar contrib iterando manualmente (ignora namespace)
            for elem in root.iter():
                tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                
                if tag_name == 'contrib':
                    # Buscar name dentro do contrib
                    for child in elem:
                        child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                        if child_tag == 'name':
                            surname = None
                            given = None
                            for grandchild in child:
                                gc_tag = grandchild.tag.split('}')[-1] if '}' in grandchild.tag else grandchild.tag
                                if gc_tag == 'surname' and grandchild.text:
                                    surname = grandchild.text
                                elif gc_tag == 'given-names' and grandchild.text:
                                    given = grandchild.text
                            
                            if surname:
                                author_name = f"{given} {surname}" if given else surname
                                data['authors'].append(author_name)
                            break
                
                elif tag_name == 'aff':
                    # Extrair texto da afiliação
                    aff_text = JAATSParser._extract_text(elem)
                    if aff_text and len(aff_text) > 5:
                        data['institutions'].add(aff_text)
            
            data['institutions'] = list(data['institutions'])
            
            return data
            
        except ET.ParseError as e:
            print(f"   [AVISO] Erro ao parsear front matter: {e}")
            return {'authors': [], 'institutions': []}
    
    @staticmethod
    def parse_xml(xml_content: str) -> Dict[str, Any]:
        """
        Parse XML JATS para extrair conteúdo estruturado.
        
        Args:
            xml_content: XML string em formato JATS
            
        Returns:
            Dicionário com seções do artigo
        """
        try:
            root = ET.fromstring(xml_content)
            
            # Se for OAI-PMH envelope, extrair o artigo de dentro
            if 'OAI-PMH' in root.tag or 'oai' in root.tag.lower():
                # Navegar: OAI-PMH -> GetRecord -> record -> metadata -> article
                article_elem = root.find('.//{http://dtd.nlm.nih.gov/ncbi/pmc/articleset/nlm-articleset-2.0/}article')
                if article_elem is None:
                    # Tentar sem namespace
                    article_elem = root.find('.//article')
                
                if article_elem is None:
                    # Tentar buscar qualquer elemento que pareça ser o artigo
                    for elem in root.iter():
                        tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                        if tag_name == 'article':
                            article_elem = elem
                            break
                
                if article_elem is not None:
                    root = article_elem
                else:
                    # Tentar usar o metadata como root
                    metadata_elem = root.find('.//{http://www.openarchives.org/OAI/2.0/}metadata')
                    if metadata_elem is not None and len(list(metadata_elem)) > 0:
                        root = list(metadata_elem)[0]
                    else:
                        return {}
            
            # Extrair namespace do root se presente
            namespace = None
            if '}' in root.tag:
                namespace = root.tag.split('}')[0][1:]  # Remove '{' do início
            
            data = {}
            
            # Abstract - buscar sem namespace (mais robusto)
            abstract_elem = root.find('.//abstract')
            if abstract_elem is None and namespace:
                # Tentar com namespace
                abstract_elem = root.find('.//{%s}abstract' % namespace)
            
            if abstract_elem is not None:
                abstract_text = JAATSParser._extract_text(abstract_elem)
                data['abstract'] = abstract_text
            else:
                print(f"   [DEBUG] Abstract não encontrado no XML")
            
            # Introduction
            intro = JAATSParser._find_section(root, 'intro', 'Introduction')
            if intro is not None:
                data['introduction'] = JAATSParser._extract_text(intro)
            
            # Methods
            methods = JAATSParser._find_section(root, 'methods', 'Methods')
            if methods is not None:
                data['methods'] = JAATSParser._extract_text(methods)
            
            # Results
            results = JAATSParser._find_section(root, 'results', 'Results')
            if results is not None:
                data['results'] = JAATSParser._extract_text(results)
            
            # Discussion
            discussion = JAATSParser._find_section(root, 'discussion', 'Discussion')
            if discussion is not None:
                data['discussion'] = JAATSParser._extract_text(discussion)
            
            # Autores e afiliações - iterar manualmente para ignorar namespaces
            authors = []
            institutions = set()
            
            # Buscar contrib iterando manualmente
            contrib_count = 0
            for elem in root.iter():
                tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                
                if tag_name == 'contrib':
                    contrib_count += 1
                    # Buscar name dentro do contrib
                    for child in elem:
                        child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                        if child_tag == 'name':
                            surname = None
                            given = None
                            for grandchild in child:
                                gc_tag = grandchild.tag.split('}')[-1] if '}' in grandchild.tag else grandchild.tag
                                if gc_tag == 'surname' and grandchild.text:
                                    surname = grandchild.text
                                elif gc_tag == 'given-names' and grandchild.text:
                                    given = grandchild.text
                            
                            if surname:
                                author_name = f"{given} {surname}" if given else surname
                                authors.append(author_name)
                            break
                
                elif tag_name == 'aff':
                    aff_text = JAATSParser._extract_text(elem)
                    if aff_text and len(aff_text) > 5:
                        institutions.add(aff_text)
            
            data['authors'] = authors
            data['institutions'] = list(institutions)
            
            # Texto completo (concatenação de todas as seções)
            full_text_parts = []
            for section in ['abstract', 'introduction', 'methods', 'results', 'discussion']:
                if section in data:
                    full_text_parts.append(data[section])
            data['full_text'] = '\n\n'.join(full_text_parts)
            
            return data
            
        except ET.ParseError as e:
            print(f"[ERRO] Falha ao parsear XML JATS: {e}")
            return {}
    
    @staticmethod
    def _find_section(root, sec_type: str, title_text: str):
        """
        Encontra seção por sec-type ou título.
        
        Args:
            root: Elemento raiz XML
            sec_type: Valor do atributo sec-type
            title_text: Texto do título da seção
            
        Returns:
            Elemento da seção ou None
        """
        # Tentar por atributo sec-type (sem namespace)
        section = root.find(f".//sec[@sec-type='{sec_type}']")
        if section is not None:
            return section
        
        # Tentar por título (iterar manualmente)
        for sec in root.findall('.//sec'):
            title_elem = sec.find('title')
            if title_elem is not None and title_elem.text:
                if title_text.lower() in title_elem.text.lower():
                    return sec
        
        return None
    
    @staticmethod
    def _extract_text(element) -> str:
        """Extrai texto de um elemento XML recursivamente."""
        text_parts = []
        if element.text:
            text_parts.append(element.text.strip())
        for child in element:
            text_parts.append(JAATSParser._extract_text(child))
            if child.tail:
                text_parts.append(child.tail.strip())
        return ' '.join(filter(None, text_parts))


class NLPExtractor:
    """Extrator de informações usando LLM (Google Gemini)."""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        """
        Inicializa extrator NLP.
        
        Args:
            api_key: Chave API do Google Gemini
            model: Nome do modelo a usar
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
    
    def extract_structured_info(self, content: str, title: str = "") -> Dict[str, Any]:
        """
        Extrai informações estruturadas do texto usando LLM.
        
        Args:
            content: Texto do artigo (abstract + seções)
            title: Título do artigo
            
        Returns:
            Dicionário com campos extraídos
        """
        if len(content) < 100:
            print(f"   [AVISO] Conteúdo muito curto para extração NLP: {len(content)} chars")
            return {}
        
        prompt = f"""
Analyze the following scientific article and extract the information in a structured JSON format.

TITLE: {title}

CONTENT:
{content[:4000]}

Extract and return ONLY a valid JSON with the following fields:
{{
  "summary_en": "full summary of the article in English (3-5 sentences describing objectives, methods, main results, and conclusions)",
  "objectives": [list of the main objectives of the study],
  "hypotheses": [list of tested hypotheses],
  "organisms": [list of organisms/cells studied],
  "conditions": [list of experimental conditions, e.g., microgravity, radiation],
  "methods": [list of methods/techniques used],
  "parameters_measured": [list of parameters/variables measured],
  "results_summary": "concise summary of the main results",
  "significant_findings": [list of significant findings],
  "implications": [list of practical or theoretical implications],
  "limitations": [list of study limitations],
  "future_directions": [list of suggested future directions],
  "duration": "duration of the experiment (e.g., 30 days, 6 months)",
  "sample_size": number of samples/individuals (just the number or null),
  "conditions_control": [list of control groups],
  "related_projects": [list of related projects/missions mentioned]
}}

IMPORTANT:
- Return ONLY the JSON, without additional text
- If information is not found, use [] for lists or null for single values
- Be concise and precise
- The summary_en must be in ENGLISH
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # Baixa variação
                    max_output_tokens=1500,
                )
            )
            
            # Extrair JSON da resposta
            response_text = response.text.strip()
            
            # Remover markdown code blocks se presente
            if response_text.startswith('```'):
                response_text = re.sub(r'^```(?:json)?\n', '', response_text)
                response_text = re.sub(r'\n```$', '', response_text)
            
            # Parse JSON
            extracted_data = json.loads(response_text)
            
            return extracted_data
            
        except json.JSONDecodeError as e:
            print(f"[ERRO] Falha ao parsear JSON da resposta LLM: {e}")
            print(f"[ERRO] Resposta bruta: {response_text[:500]}")
            return {}
        except Exception as e:
            print(f"[ERRO] Falha na extração NLP: {e}")
            import traceback
            traceback.print_exc()
            return {}


class DatabaseManager:
    """Gerenciador de banco de dados MongoDB."""
    
    def __init__(self, connection_string: str = "mongodb://localhost:27017/", 
                 database: str = "spaceapss", 
                 collection: str = "experiments"):
        """
        Inicializa conexão com MongoDB.
        
        Args:
            connection_string: String de conexão MongoDB
            database: Nome do database
            collection: Nome da collection
        """
        self.client = MongoClient(connection_string)
        self.db = self.client[database]
        self.collection = self.db[collection]
        
        # Criar índice único no experiment_id
        self.collection.create_index("experiment_id", unique=True)
    
    def save_article(self, article: ArticleMetadata) -> bool:
        """
        Salva artigo no banco de dados.
        
        Args:
            article: Objeto ArticleMetadata
            
        Returns:
            True se sucesso, False se já existe
        """
        try:
            document = asdict(article)
            document['updated_at'] = datetime.utcnow()
            
            # Verificar se já existe
            existing = self.collection.find_one({'experiment_id': article.experiment_id})
            
            if existing:
                # Atualizar preservando created_at
                document['created_at'] = existing.get('created_at', datetime.utcnow())
                self.collection.replace_one(
                    {'experiment_id': article.experiment_id},
                    document
                )
                print(f"✓ Artigo {article.experiment_id} atualizado no banco de dados")
            else:
                # Criar novo
                document['created_at'] = datetime.utcnow()
                self.collection.insert_one(document)
                print(f"✓ Artigo {article.experiment_id} salvo no banco de dados")
            
            return True
            
        except Exception as e:
            print(f"[ERRO] Falha ao salvar artigo {article.experiment_id}: {e}")
            return False
    
    def update_article(self, experiment_id: str, updates: Dict[str, Any]) -> bool:
        """
        Atualiza artigo existente.
        
        Args:
            experiment_id: ID do experimento
            updates: Dicionário com campos a atualizar
            
        Returns:
            True se sucesso
        """
        updates['updated_at'] = datetime.utcnow()
        result = self.collection.update_one(
            {'experiment_id': experiment_id},
            {'$set': updates}
        )
        return result.modified_count > 0
    
    def get_article(self, experiment_id: str) -> Optional[Dict]:
        """Busca artigo por ID."""
        return self.collection.find_one({'experiment_id': experiment_id})
    
    def count_articles(self) -> int:
        """Retorna total de artigos no banco."""
        return self.collection.count_documents({})


class EnrichmentPipeline:
    """Pipeline completo de enriquecimento de artigos."""
    
    def __init__(self, 
                 google_api_key: str,
                 ncbi_email: str = "your_email@example.com",
                 mongodb_uri: str = "mongodb://localhost:27017/"):
        """
        Inicializa pipeline.
        
        Args:
            google_api_key: Chave API Google Gemini
            ncbi_email: Email para NCBI API
            mongodb_uri: URI de conexão MongoDB
        """
        self.google_api_key = google_api_key
        self.ncbi_email = ncbi_email
        self.mongodb_uri = mongodb_uri
        
        self.nlp_extractor = NLPExtractor(google_api_key)
        self.db_manager = DatabaseManager(mongodb_uri)
    
    async def process_article(self, pmc_url_or_id: str) -> Optional[ArticleMetadata]:
        """
        Processa um artigo completo.
        
        Args:
            pmc_url_or_id: URL PMC ou PMCID
            
        Returns:
            ArticleMetadata ou None em caso de erro
        """
        async with NCBIAPIClient(self.ncbi_email) as ncbi_client:
            try:
                # 1. Extrair PMCID
                pmcid = ncbi_client.extract_pmcid(pmc_url_or_id)
                print(f"\n{'='*60}")
                print(f"Processando PMC{pmcid}")
                print(f"{'='*60}")
                
                # 2. Buscar metadados via ESummary
                print("→ Buscando metadados via ESummary...")
                metadata = await ncbi_client.fetch_metadata(pmcid)
                
                # Criar objeto ArticleMetadata
                article = ArticleMetadata(experiment_id=f"PMC{pmcid}")
                
                # Preencher metadados básicos
                if metadata:
                    article.title = metadata.get('title', '')
                    article.doi = metadata.get('doi', '')
                    
                    # Ano de publicação
                    pub_date = metadata.get('pubdate', '')
                    if pub_date:
                        year_match = re.search(r'\d{4}', pub_date)
                        if year_match:
                            article.year = int(year_match.group())
                    
                    # Journal
                    article.journal = metadata.get('fulljournalname', '')
                    
                    # PMID
                    pmid_list = metadata.get('articleids', [])
                    for id_obj in pmid_list:
                        if id_obj.get('idtype') == 'pmid':
                            article.pmid = id_obj.get('value')
                            break
                
                # 3. Buscar texto completo via OAI-PMH
                print("→ Buscando texto completo via OAI-PMH...")
                xml_content = await ncbi_client.fetch_fulltext_xml(pmcid)
                
                # 3.1. Buscar front matter para autores/afiliações
                print("→ Buscando front matter (autores/afiliações)...")
                front_matter_xml = await ncbi_client.fetch_front_matter(pmcid)
                
                if front_matter_xml:
                    front_data = JAATSParser.parse_front_matter(front_matter_xml)
                    if front_data.get('authors'):
                        article.authors = front_data['authors']
                    if front_data.get('institutions'):
                        article.institutions = front_data['institutions']
                
                if xml_content:
                    print("→ Parseando XML JATS...")
                    jats_data = JAATSParser.parse_xml(xml_content)
                    
                    # Atualizar artigo com dados JATS
                    if 'abstract' in jats_data:
                        article.abstract = jats_data['abstract']
                    # Se não conseguiu autores do front matter, tentar do JATS
                    if not article.authors and 'authors' in jats_data:
                        article.authors = jats_data['authors']
                    if not article.institutions and 'institutions' in jats_data:
                        article.institutions = jats_data['institutions']
                    if 'full_text' in jats_data:
                        article.full_text = jats_data['full_text']
                
                # 4. Buscar detalhes adicionais do PubMed (se tiver PMID)
                if article.pmid:
                    print(f"→ Buscando detalhes do PubMed (PMID: {article.pmid})...")
                    pubmed_data = await ncbi_client.fetch_pubmed_details(article.pmid)
                    if pubmed_data:
                        article.mesh_terms = pubmed_data.get('mesh_terms', [])
                        article.funding.extend(pubmed_data.get('funding', []))
                
                # 5. Extração NLP com LLM
                if article.full_text or article.abstract:
                    print("→ Extraindo informações estruturadas com LLM...")
                    content_for_nlp = article.full_text or article.abstract
                    
                    nlp_data = self.nlp_extractor.extract_structured_info(
                        content_for_nlp, 
                        article.title or ""
                    )
                    
                    # Atualizar artigo com dados NLP
                    if nlp_data:
                        article.summary_en = nlp_data.get('summary_en', '')
                        article.objectives = nlp_data.get('objectives', [])
                        article.hypotheses = nlp_data.get('hypotheses', [])
                        article.organisms = nlp_data.get('organisms', [])
                        article.conditions = nlp_data.get('conditions', [])
                        article.methods = nlp_data.get('methods', [])
                        article.parameters_measured = nlp_data.get('parameters_measured', [])
                        article.results_summary = nlp_data.get('results_summary', '')
                        article.significant_findings = nlp_data.get('significant_findings', [])
                        article.implications = nlp_data.get('implications', [])
                        article.limitations = nlp_data.get('limitations', [])
                        article.future_directions = nlp_data.get('future_directions', [])
                        article.duration = nlp_data.get('duration', '')
                        article.sample_size = nlp_data.get('sample_size')
                        article.conditions_control = nlp_data.get('conditions_control', [])
                        article.related_projects = nlp_data.get('related_projects', [])
                    else:
                        print("   [AVISO] Nenhum dado extraído pelo LLM!")
                else:
                    print("   [AVISO] Sem texto para extração NLP (sem full_text nem abstract)")
                
                # 6. Salvar no banco de dados
                print("→ Salvando no banco de dados...")
                self.db_manager.save_article(article)
                
                print(f"✓ Processamento concluído para PMC{pmcid}")
                return article
                
            except Exception as e:
                print(f"[ERRO] Falha ao processar {pmc_url_or_id}: {e}")
                import traceback
                traceback.print_exc()
                return None
    
    async def process_batch(self, pmc_list: List[str], delay: float = 0.5):
        """
        Processa lista de artigos em batch.
        
        Args:
            pmc_list: Lista de URLs ou PMCIDs
            delay: Delay entre requisições (segundos)
        """
        total = len(pmc_list)
        
        successful = 0
        failed = 0
        
        for idx, pmc_id in enumerate(pmc_list, 1):
            print(f"\n[{idx}/{total}] Processando: {pmc_id}")
            
            result = await self.process_article(pmc_id)
            
            if result:
                successful += 1
            else:
                failed += 1
            
            # Delay para não sobrecarregar APIs
            if idx < total:
                await asyncio.sleep(delay)
        
        print(f"\n{'#'*60}")
        print(f"PROCESSAMENTO CONCLUÍDO")
        print(f"Total: {total} | Sucesso: {successful} | Falha: {failed}")
        print(f"Artigos no banco: {self.db_manager.count_articles()}")
        print(f"{'#'*60}\n")


# Funções auxiliares para uso direto

async def process_single_article(pmc_url: str, 
                                 google_api_key: str,
                                 ncbi_email: str = "your_email@example.com",
                                 mongodb_uri: str = "mongodb://localhost:27017/") -> Optional[ArticleMetadata]:
    """
    Processa um único artigo.
    
    Args:
        pmc_url: URL ou PMCID
        google_api_key: Chave API Google
        ncbi_email: Email para NCBI
        mongodb_uri: URI MongoDB
        
    Returns:
        ArticleMetadata ou None
    """
    pipeline = EnrichmentPipeline(google_api_key, ncbi_email, mongodb_uri)
    return await pipeline.process_article(pmc_url)


async def process_from_csv(csv_path: str,
                           google_api_key: str,
                           ncbi_email: str = "your_email@example.com",
                           mongodb_uri: str = "mongodb://localhost:27017/"):
    """
    Processa artigos de arquivo CSV.
    
    Args:
        csv_path: Caminho do CSV (deve ter coluna 'Link')
        google_api_key: Chave API Google
        ncbi_email: Email para NCBI
        mongodb_uri: URI MongoDB
    """
    import pandas as pd
    
    df = pd.read_csv(csv_path)
    
    if 'Link' not in df.columns:
        raise ValueError("CSV deve conter coluna 'Link'")
    
    pmc_links = df['Link'].dropna().tolist()
    
    pipeline = EnrichmentPipeline(google_api_key, ncbi_email, mongodb_uri)
    await pipeline.process_batch(pmc_links)


if __name__ == "__main__":
    # Exemplo de uso
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    NCBI_EMAIL = "your_email@example.com"
    MONGODB_URI = "mongodb://localhost:27017/"
    
    # Processar CSV
    asyncio.run(process_from_csv(
        csv_path="shared/SB_publication_PMC.csv",
        google_api_key=GOOGLE_API_KEY,
        ncbi_email=NCBI_EMAIL,
        mongodb_uri=MONGODB_URI
    ))
