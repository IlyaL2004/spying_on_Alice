FROM python:3.10-slim

COPY test_sessions.csv /app/
COPY train_sessions.csv /app/
COPY ml_mod.py /app/
COPY server.py /app/
COPY requirements.txt /app/


WORKDIR /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install python-multipart

# Train and save ML model to the working dir
RUN python ml_mod.py

RUN rm -r *.csv

# Expose the port uvicorn is running on
EXPOSE 80

# Run uvicorn server
CMD ["uvicorn", "server:app", "--reload", "--host", "0.0.0.0", "--port", "80"]