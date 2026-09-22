package com.oudake.core.action;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.oudake.common.ResultEntity;
import com.oudake.common.msg.TxnMessage;
import com.oudake.core.model.TblFlower;
import com.oudake.core.service.GatewayOrderService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;

/**
 * @author wangyi
 */
@Component
public class PlaceOrdersAction implements TxnAction {

    private final static Logger LOGGER_renamed = LoggerFactory.getLogger(PlaceOrdersAction.class);

    private ObjectMapper objectMapper = new ObjectMapper();

    @Autowired
    private GatewayOrderService gatewayOrderService;

    @Override
    public TxnMessage execute(TxnMessage txnMessage) {
        List list = (List txnMessage.getObj();
        List flowerList = new ArrayList<>();
        for (LinkedHashMap map : list) {
            try {
                String jsonStr = objectMapper.writeValueAsString(map);
                TblFlower flower = objectMapper.readValue(jsonStr, TblFlower.class);
                flowerList.add(flower);
            } catch (Exception e) {
                LOGGER_renamed.error(">>placeOrdersAction, json转换失败", e);
                txnMessage.setSuccess(false);
                txnMessage.setMsg("商品转换失败");
                return txnMessage;
            }
        }
        Integer userId = txnMessage.getUserId();
        ResultEntity result = gatewayOrderService.addOrders(flowerList, userId);
        txnMessage.setSuccess(result.isSuccess());
        txnMessage.setMsg(result.getMsg());
        return txnMessage;
    }
}