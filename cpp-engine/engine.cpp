#include <iostream>
#include <chrono>
#include <thread>
#include <mutex>
#include <mqtt/async_client.h>

const std::string SERVER_ADDRESS = "tcp://mqtt:1883";
const std::string CLIENT_ID = "cpp_engine";
const std::string TOPIC_MOVIMENTO = "eventos/movimento";
const std::string TOPIC_ALERTA = "alertas/inatividade";

const int INACTIVITY_LIMIT = 30; // segundos

std::chrono::steady_clock::time_point last_event_time;
std::mutex time_mutex;

mqtt::async_client* global_client = nullptr;

class Callback : public virtual mqtt::callback {
public:
    void message_arrived(mqtt::const_message_ptr msg) override {

        std::lock_guard<std::mutex> lock(time_mutex);
        last_event_time = std::chrono::steady_clock::now();

        std::cout << "Evento recebido: "
                  << msg->to_string()
                  << std::endl;
    }
};

void publish_alert(int duration) {

    if (!global_client) return;

    std::string payload =
        "Inatividade detectada: " +
        std::to_string(duration) +
        " segundos sem movimento";

    auto message = mqtt::make_message(TOPIC_ALERTA, payload);
    message->set_qos(1);

    try {
        global_client->publish(message)->wait();
        std::cout << "Alerta publicado no MQTT." << std::endl;
    } catch (const mqtt::exception& e) {
        std::cerr << "Erro ao publicar alerta: "
                  << e.what()
                  << std::endl;
    }
}

void monitor_inactivity() {

    while (true) {

        std::this_thread::sleep_for(std::chrono::seconds(5));

        std::lock_guard<std::mutex> lock(time_mutex);

        auto now = std::chrono::steady_clock::now();
        auto duration =
            std::chrono::duration_cast<std::chrono::seconds>(
                now - last_event_time
            ).count();

        if (duration > INACTIVITY_LIMIT) {
            std::cout << "Inatividade detectada."
                      << std::endl;

            publish_alert(duration);

            last_event_time = std::chrono::steady_clock::now();
        }
    }
}

int main() {

    last_event_time = std::chrono::steady_clock::now();

    mqtt::async_client client(SERVER_ADDRESS, CLIENT_ID);
    global_client = &client;

    Callback cb;
    client.set_callback(cb);

    try {

        std::cout << "Conectando ao broker..." << std::endl;
        client.connect()->wait();

        std::cout << "Inscrito no tópico de movimento..."
                  << std::endl;

        client.subscribe(TOPIC_MOVIMENTO, 1)->wait();

        std::thread monitor_thread(monitor_inactivity);
        monitor_thread.join();

    } catch (const mqtt::exception& exc) {
        std::cerr << "Erro MQTT: "
                  << exc.what()
                  << std::endl;
        return 1;
    }

    return 0;
}
