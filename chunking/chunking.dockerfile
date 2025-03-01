FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /app

COPY main.py /app/

RUN pip install pypdf fastapi

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]