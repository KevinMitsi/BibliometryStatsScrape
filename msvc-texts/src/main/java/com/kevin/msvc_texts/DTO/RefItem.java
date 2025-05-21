
package com.kevin.msvc_texts.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.JsonNode;
import lombok.EqualsAndHashCode;

@EqualsAndHashCode
public class RefItem {

    @JsonProperty("title")
    private JsonNode title;

    @JsonProperty("abstract")
    private JsonNode abstractField;

    public RefItem() { }

    public RefItem(JsonNode abstractField, JsonNode title) {
        this.abstractField = abstractField;
        this.title = title;
    }

    /**
     * Devuelve siempre un String: si el nodo es textual, devuelve su texto;
     * si es un objeto o array, devuelve su JSON serializado.
     */
    public String getAbstractText() {
        if (abstractField == null || abstractField.isNull()) {
            return null;
        }
        if (abstractField.isTextual()) {
            return abstractField.asText();
        }
        // para objetos/arrays: serializa como JSON
        return abstractField.toString();
    }

    public String getTittleText() {
        if (title == null || title.isNull()) {
            return null;
        }
        if (title.isTextual()) {
            return title.asText();
        }
        // para objetos/arrays: serializa como JSON
        return title.toString();
    }

    public void setAbstractField(JsonNode abstractField) {
        this.abstractField = abstractField;
    }

    @Override
    public String toString() {
        return "RefItem{abstract=" + getAbstractText() + "}";
    }
}
