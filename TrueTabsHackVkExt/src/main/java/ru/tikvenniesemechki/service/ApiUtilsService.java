package ru.tikvenniesemechki.service;

import io.github.cdimascio.dotenv.Dotenv;
import okhttp3.HttpUrl;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

import java.io.IOException;

import static ru.tikvenniesemechki.config.Config.API_URL_USER_GET;
import static ru.tikvenniesemechki.config.Config.API_VERSION;

public class ApiUtilsService {
    private final static OkHttpClient client = new OkHttpClient();
    private final static Dotenv dotenv = Dotenv.load();

    public static Response getVkUser(int vkUserId) throws IOException {
        HttpUrl getUserUrl = HttpUrl.parse(API_URL_USER_GET).newBuilder()
                .addQueryParameter("user_ids", String.valueOf(vkUserId))
                .addQueryParameter("fields", "screen_name,photo_200")
                .addQueryParameter("access_token", dotenv.get("AccessToken"))
                .addQueryParameter("v", API_VERSION)
                .build();

        Request getUserRequest = new Request.Builder()
                .url(getUserUrl)
                .build();

        return client.newCall(getUserRequest).execute();
    }
}
