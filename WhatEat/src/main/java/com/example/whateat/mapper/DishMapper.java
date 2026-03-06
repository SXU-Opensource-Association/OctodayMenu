package com.example.whateat.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.whateat.entity.Dish;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface DishMapper extends BaseMapper<Dish> {
}
