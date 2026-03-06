package com.example.whateat.entity;

import java.util.ArrayList;
import java.util.List;

public class DishTag {
    private int id;
    private String tagName;
    private List<Dish> dishList;

    public DishTag(){
        this.dishList = new ArrayList<Dish>();
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getTagName() {
        return tagName;
    }

    public void setTagName(String tagName) {
        this.tagName = tagName;
    }

    public List<Dish> getDishList() {
        return dishList;
    }

    public void setDishList(List<Dish> dishList) {
        this.dishList = dishList;
    }
}
