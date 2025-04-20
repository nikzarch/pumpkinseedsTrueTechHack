package ru.tikvenniesemechki.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.github.cdimascio.dotenv.Dotenv;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import okhttp3.*;
import org.apache.commons.text.StringEscapeUtils;
import ru.tikvenniesemechki.model.Purchase;

import java.io.IOException;
import java.net.http.HttpResponse;
import java.util.*;

import static ru.tikvenniesemechki.config.Config.*;
import static ru.tikvenniesemechki.service.RequestService.getSku;

@Slf4j
public class MassageHandlerService {
    private volatile boolean running = false;

    OkHttpClient client = new OkHttpClient();
    ObjectMapper mapper = new ObjectMapper();
    Dotenv dotenv = Dotenv.load();

    public void stop() {
        running = false;
    }

    public void startMassageHandler() {
        running = true;

        HttpUrl url = HttpUrl.parse(API_URL_LONGPOLL).newBuilder()
                .addQueryParameter("group_id", dotenv.get("GroupId"))
                .addQueryParameter("access_token", dotenv.get("AccessToken"))
                .addQueryParameter("v", API_VERSION)
                .build();

        Request request = new Request.Builder().url(url).get().build();

        try (Response response = client.newCall(request).execute()) {
            if (response.body() == null) {
                return;
            }

            JsonNode jsonResponse = mapper.readTree(response.body().string());
            if (jsonResponse.has("response")) {
                JsonNode responseObj = jsonResponse.get("response");
                String server = responseObj.get("server").asText();
                String key = responseObj.get("key").asText();
                int ts = responseObj.get("ts").asInt();

                listenForMessages(server, key, ts);
            }
        } catch (IOException e) {
            log.atError().log("Ошибка при получении Long Poll сервера");
        }

    }

    public void listenForMessages(String server, String key, int ts) {
        OkHttpClient client = new OkHttpClient();

        while (running) {
            HttpUrl url = HttpUrl.parse(server).newBuilder()
                    .addQueryParameter("act", "a_check")
                    .addQueryParameter("key", key)
                    .addQueryParameter("ts", String.valueOf(ts))
                    .addQueryParameter("wait", "25")
                    .addQueryParameter("mode", "2")
                    .addQueryParameter("version", API_VERSION)
                    .build();

            Request request = new Request.Builder().url(url).get().build();

            try (Response response = client.newCall(request).execute()) {
                if (response.body() == null) {
                    continue;
                }

                JsonNode jsonResponse = mapper.readTree(response.body().string());
                ts = jsonResponse.get("ts").asInt();

                JsonNode updates = jsonResponse.get("updates");
                if (!updates.isArray()) {
                    continue;
                }

                for (JsonNode update : updates) {
                    if (update.get("type").asText().equals("message_new")) {
                        JsonNode message = update.get("object").get("message");
                        processMessage(message);
                    }
                }
            } catch (IOException | InterruptedException e) {
                log.atError().log("Ошибка при ожидании сообщении");
            }
        }
    }

    public void processMessage(JsonNode message) throws IOException, InterruptedException {
        int vkUserId = message.get("from_id").asInt();
        String text = message.get("text").asText();

        ResponseBody result = ApiUtilsService.getVkUser(vkUserId).body();
        if (result == null) {
            return;
        }

        JsonNode jsonUser = mapper.readTree(result.string());

        String name = jsonUser.get("response").get(0).get("first_name").asText() + " " +
                jsonUser.get("response").get(0).get("last_name").asText();
        String userName = jsonUser.get("response").get(0).get("screen_name").asText();

        System.out.println(message.toPrettyString());

        for (JsonNode file: message.get("attachments")){
            if (Objects.equals(file.get("type").asText(), "market")){
                String sku = file.get("market").get("sku").asText();

                System.out.println(file.toPrettyString());

                Purchase purchase = new Purchase();
                String escapedJson = StringEscapeUtils.escapeJson(text);
                purchase.setMassage(escapedJson);
                purchase.setCustomerName(name);
                purchase.setCustomerLink(VK_PROFILE_URL + userName);

                JsonNode jsonNodeGoods = mapper.readTree(getSku().body());
                jsonNodeGoods = jsonNodeGoods.get("data").get("records");

                String sku_id = null;

                for(JsonNode jsonNodeGood: jsonNodeGoods){
                    if (Objects.equals(jsonNodeGood.get("fields").get("SKU (ID товара)").asText(), sku)){
                        sku_id = jsonNodeGood.get("recordId").asText();
                    }
                }

                purchase.setSkuId(sku_id);

                HttpResponse<String> response = RequestService.setPurchase(purchase);
                System.out.println(response.body());
            }
        }
    }

}
