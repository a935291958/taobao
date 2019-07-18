/*
Navicat MySQL Data Transfer

Source Server         : 127.0.0.1
Source Server Version : 50554
Source Host           : 127.0.0.1:3306
Source Database       : taobao

Target Server Type    : MYSQL
Target Server Version : 50554
File Encoding         : 65001

Date: 2019-07-16 16:56:30
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for tb_shop
-- ----------------------------
DROP TABLE IF EXISTS `tb_shop`;
CREATE TABLE `tb_shop` (
  `nid` int(11) NOT NULL AUTO_INCREMENT,
  `comment_url` varchar(255) DEFAULT NULL COMMENT '注释链接',
  `detail_url` varchar(255) DEFAULT NULL COMMENT '详情链接',
  `nick` varchar(255) DEFAULT NULL COMMENT '店铺名称',
  `item_loc` varchar(255) DEFAULT NULL COMMENT '地址',
  `pic_url` varchar(255) DEFAULT NULL COMMENT '大图',
  `raw_title` varchar(255) DEFAULT NULL COMMENT '原标题',
  `title` varchar(255) DEFAULT NULL COMMENT '显示的标题',
  `view_sales` varchar(255) DEFAULT NULL COMMENT '付款人数',
  `view_price` decimal(10,2) DEFAULT NULL COMMENT '显示的价格',
  `addtime` datetime DEFAULT NULL,
  PRIMARY KEY (`nid`)
) ENGINE=MyISAM AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4;
