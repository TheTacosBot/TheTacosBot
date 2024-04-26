FROM 3.9.19-slim

ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . src
CMD [ "python", "./src/main.py" ]
