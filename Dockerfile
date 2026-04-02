FROM debian:bullseye-slim

WORKDIR /archipelago

RUN apt update && apt-get install wget -y

RUN wget https://github.com/ArchipelagoMW/Archipelago/releases/download/0.6.7/Archipelago_0.6.7_linux-x86_64.tar.gz &&\
  tar -xf Archipelago_0.6.7_linux-x86_64.tar.gz &&\
  rm Archipelago_0.6.7_linux-x86_64.tar.gz

RUN echo "if [ ! -f /archipelago/Archipelago/output/AP_*.zip ]; then" >> /archipelago/startup.sh &&\
    echo "  /archipelago/Archipelago/ArchipelagoGenerate" >> /archipelago/startup.sh &&\
    echo "fi" >> /archipelago/startup.sh &&\
    echo "/archipelago/Archipelago/ArchipelagoServer /archipelago/Archipelago/output/AP_*.zip" >> /archipelago/startup.sh &&\
  chmod +x /archipelago/startup.sh

CMD ["sh", "/archipelago/startup.sh"]
