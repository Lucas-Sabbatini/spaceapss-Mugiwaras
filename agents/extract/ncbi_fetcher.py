"""
Fetcher específico para artigos do NCBI PubMed Central (PMC).
Usa a API oficial E-utilities para evitar bloqueios por scraping.
"""

import aiohttp
import asyncio
from xml.etree import ElementTree as ET
from typing import Dict, Optional


async def fetch_pmc_article(pmc_id: str) -> Optional[Dict[str, str]]:
    """
    Busca um artigo do PMC usando a API E-utilities do NCBI.
    
    Args:
        pmc_id: ID do artigo PMC (ex: 'PMC4136787' ou apenas '4136787')
        
    Returns:
        Dicionário com 'abstract' e 'content', ou None se falhar
    """
    # Remover prefixo 'PMC' se existir
    if pmc_id.startswith('PMC'):
        pmc_id = pmc_id[3:]
    
    # URL da API E-utilities para buscar o artigo completo em XML
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        'db': 'pmc',
        'id': pmc_id,
        'retmode': 'xml'
    }
    
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Delay para respeitar as políticas do NCBI (máximo 3 req/segundo)
            await asyncio.sleep(0.4)
            
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    print(f"  [ERRO NCBI API] Status {resp.status} para PMC{pmc_id}")
                    return None
                
                xml_content = await resp.text()
                
                # Parse do XML
                root = ET.fromstring(xml_content)
                
                # Extrair abstract
                abstract = extract_abstract(root)
                
                # Extrair conteúdo completo (body)
                content = extract_body(root)
                
                if not abstract and not content:
                    print(f"  [AVISO] Artigo PMC{pmc_id} sem abstract ou conteúdo")
                    return None
                
                return {
                    'abstract': abstract or '',
                    'content': content or ''
                }
                
    except asyncio.TimeoutError:
        print(f"  [ERRO] Timeout ao buscar PMC{pmc_id}")
        return None
    except ET.ParseError as e:
        print(f"  [ERRO] Falha ao parsear XML do PMC{pmc_id}: {e}")
        return None
    except Exception as e:
        print(f"  [ERRO] Exceção ao buscar PMC{pmc_id}: {e}")
        return None


def extract_abstract(root: ET.Element) -> str:
    """Extrai o abstract do XML do PMC."""
    abstract_parts = []
    
    # Procura por elementos <abstract>
    for abstract in root.findall('.//abstract'):
        # Pega todos os parágrafos dentro do abstract
        for p in abstract.findall('.//p'):
            text = ''.join(p.itertext()).strip()
            if text:
                abstract_parts.append(text)
    
    return '\n\n'.join(abstract_parts)


def extract_body(root: ET.Element) -> str:
    """Extrai o conteúdo principal (body) do XML do PMC."""
    body_parts = []
    
    # Procura pelo elemento <body>
    body = root.find('.//body')
    if body is not None:
        # Processa cada seção
        for sec in body.findall('.//sec'):
            # Título da seção
            title = sec.find('title')
            if title is not None:
                title_text = ''.join(title.itertext()).strip()
                if title_text:
                    body_parts.append(f"\n{title_text}\n")
            
            # Parágrafos da seção
            for p in sec.findall('.//p'):
                text = ''.join(p.itertext()).strip()
                if text:
                    body_parts.append(text)
    
    return '\n\n'.join(body_parts)


def extract_pmc_id_from_url(url: str) -> Optional[str]:
    """
    Extrai o ID do PMC de uma URL.
    
    Args:
        url: URL do artigo (ex: 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4136787/')
        
    Returns:
        ID do PMC (ex: '4136787') ou None se não encontrar
    """
    import re
    
    # Padrão para encontrar PMC seguido de números
    match = re.search(r'PMC(\d+)', url)
    if match:
        return match.group(1)
    
    return None


async def fetch_pmc_from_url(url: str) -> Optional[Dict[str, str]]:
    """
    Wrapper que extrai o PMC ID da URL e busca o artigo.
    
    Args:
        url: URL completa do artigo PMC
        
    Returns:
        Dicionário com 'abstract' e 'content', ou None se falhar
    """
    pmc_id = extract_pmc_id_from_url(url)
    if not pmc_id:
        print(f"  [ERRO] Não foi possível extrair PMC ID da URL: {url}")
        return None
    
    print(f"  Buscando via NCBI API: PMC{pmc_id}")
    return await fetch_pmc_article(pmc_id)
