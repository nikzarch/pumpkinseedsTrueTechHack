package ru.tikvenniesemechki.service;

import io.github.cdimascio.dotenv.Dotenv;
import okhttp3.Request;
import ru.tikvenniesemechki.model.Purchase;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class RequestService {
    private static final Dotenv dotenv = Dotenv.load();

    public static HttpResponse<String> setPurchase(Purchase purchase)
            throws IOException, InterruptedException {

        HttpClient client = HttpClient.newHttpClient();

        String json = String.format("""
                {
                  "records": [
                  {
                    "fields": {
                      "Сообщение": "%s",
                      "Имя покупателя": "%s",
                      "Ссылка на покупателя": "%s",
                      "Артикул товара": ["%s"],
                      "Статус": "Не обработан",
                      "Источник": "VK"
                    }
                  }
                ],
                  "fieldKey": "name"
                }
                """,
                purchase.getMassage(),
                purchase.getCustomerName(),
                purchase.getCustomerLink(),
                purchase.getSkuId()
        );

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("https://true.tabs.sale/fusion/v1/datasheets/dstjMx0dGhjoaWol2N/records?viewId=viwY4Gtwi0jrp&fieldKey=name"))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + dotenv.get("Token"))
                .POST(HttpRequest.BodyPublishers.ofString(json))
                .build();


        
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

        return response;
    }

    public static HttpResponse<String> getSku()
            throws IOException, InterruptedException {

        HttpClient client = HttpClient.newHttpClient();


        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("https://true.tabs.sale/fusion/v1/datasheets/dstR95kW46WwtnVxnw/records?viewId=viwj37ePoX8uk&fieldKey=name"))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + dotenv.get("Token"))
                .GET()
                .build();


        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

        return response;
    }
}
