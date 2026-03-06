package com.example.whateat.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.fasterxml.jackson.annotation.JsonBackReference;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

public class Dish {
    private int id;
    private String dname;
    private Integer restaurantId;
    private BigDecimal price;
    private String photo;
    private Integer status;
    private BigDecimal rate;
    private Date updateTime;
    @JsonBackReference
    @TableField(exist=false)
    private Restaurant restaurant;
    @TableField(exist=false)
    private List<Comment> commentList;
    @TableField(exist=false)
    private List<DishTag> dishTagList;

    public Dish(){
        this.commentList = new ArrayList<Comment>();
        this.dishTagList = new ArrayList<DishTag>();
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getDname() {
        return dname;
    }

    public void setDname(String dname) {
        this.dname = dname;
    }

    public Integer getRestaurantId() {
        return restaurantId;
    }

    public void setRestaurantId(Integer restaurantId) {
        this.restaurantId = restaurantId;
    }

    public BigDecimal getPrice() {
        return price;
    }

    public void setPrice(BigDecimal price) {
        this.price = price;
    }

    public String getPhoto() {
        return photo;
    }

    public void setPhoto(String photo) {
        this.photo = photo;
    }

    public Integer getStatus() {
        return status;
    }

    public void setStatus(Integer status) {
        this.status = status;
    }

    public BigDecimal getRate() {
        return rate;
    }

    public void setRate(BigDecimal rate) {
        this.rate = rate;
    }

    public Date getUpdateTime() {
        return updateTime;
    }

    public void setUpdateTime(Date updateTime) {
        this.updateTime = updateTime;
    }

    public Restaurant getRestaurant() {
        return restaurant;
    }

    public void setRestaurant(Restaurant restaurant) {
        this.restaurant = restaurant;
    }

    public List<Comment> getCommentList() {
        return commentList;
    }

    public void setCommentList(List<Comment> commentList) {
        this.commentList = commentList;
    }

    public List<DishTag> getDishTagList() {
        return dishTagList;
    }

    public void setDishTagList(List<DishTag> dishTagList) {
        this.dishTagList = dishTagList;
    }
}
