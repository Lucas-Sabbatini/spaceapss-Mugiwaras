FROM python:3.12-slim

WORKDIR /app

COPY ./pyproject.toml /app/pyproject.toml
RUN pip install --no-cache-dir --upgrade -e .

COPY ./packages /app/packages
COPY ./extract /app/extract
COPY ./shared /app/shared
COPY ./build_knowledge_graph.py /app/build_knowledge_graph.py
#RUN python build_knowledge_graph.py #Esta linha está comentada pois no ambiente de dev as variáveis de ambiente não estão setadas,
# por isso essa parte do código é executada na instânicia da imagem do container no docker-compose.yml

EXPOSE 8000

CMD ["uvicorn", "packages.api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]