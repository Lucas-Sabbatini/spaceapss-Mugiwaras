FROM python:3.12-slim

WORKDIR /app

COPY ./pyproject.toml /app/pyproject.toml
RUN pip install --no-cache-dir --upgrade -e .

COPY ./packages /app/packages
COPY ./extract /app/extract
COPY ./shared /app/shared
COPY ./build_knowledge_graph.py /app/build_knowledge_graph.py
COPY ./startup.sh /app/startup.sh

RUN chmod +x /app/startup.sh

EXPOSE 8080

CMD ["/app/startup.sh"]