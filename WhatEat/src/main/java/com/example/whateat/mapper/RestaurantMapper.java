package com.example.whateat.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.whateat.entity.Restaurant;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface RestaurantMapper extends BaseMapper<Restaurant> {
}
