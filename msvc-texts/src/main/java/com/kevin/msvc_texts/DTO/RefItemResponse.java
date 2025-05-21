// RefItemResponse.java
package com.kevin.msvc_texts.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class RefItemResponse {
    public RefItemResponse() {
    }

    public RefItemResponse(String status, List<RefItem> data) {
        this.status = status;
        this.data = data;
    }

    @JsonProperty("status")
    private String status;

    @JsonProperty("data")
    private List<RefItem> data;

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public List<RefItem> getData() {
        return data;
    }

    public void setData(List<RefItem> data) {
        this.data = data;
    }
}
