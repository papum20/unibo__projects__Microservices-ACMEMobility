FROM jolielang/jolie:latest

WORKDIR /srv/bank

COPY bank.ol .
COPY bank.wsdl .

# REST pour les workers Python (aligné avec docker-compose du collègue)
EXPOSE 8000
# SOAP pour Camunda direct
EXPOSE 8080

CMD ["jolie", "bank.ol"]
