package ru.tikvenniesemechki.model;

import lombok.Data;

@Data
public class Purchase {
    private String sku;
    private String customerName;
    private String customerLink;
    private String massage;
}
