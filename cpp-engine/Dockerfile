FROM gcc:13

WORKDIR /app

# Instala dependências MQTT
RUN apt update && apt install -y \
    cmake \
    git \
    libssl-dev

# Instala biblioteca Paho MQTT C
RUN git clone https://github.com/eclipse/paho.mqtt.c.git \
    && cd paho.mqtt.c \
    && cmake -Bbuild -H. -DPAHO_WITH_SSL=ON \
    && cmake --build build/ --target install \
    && ldconfig

# Instala biblioteca Paho MQTT C++
RUN git clone https://github.com/eclipse/paho.mqtt.cpp.git \
    && cd paho.mqtt.cpp \
    && cmake -Bbuild -H. \
    && cmake --build build/ --target install \
    && ldconfig

COPY engine.cpp .

RUN g++ engine.cpp -o engine -lpaho-mqttpp3 -lpaho-mqtt3as -lpthread

CMD ["./engine"]
