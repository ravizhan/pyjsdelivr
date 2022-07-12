/*
 Navicat Premium Data Transfer

 Source Server         : pyjsd
 Source Server Type    : MySQL
 Source Server Version : 50737
 Source Host           : 192.168.3.132:3306
 Source Schema         : pyjsd

 Target Server Type    : MySQL
 Target Server Version : 50737
 File Encoding         : 65001

 Date: 04/07/2022 19:56:07
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for blacklist
-- ----------------------------
DROP TABLE IF EXISTS `blacklist`;
CREATE TABLE `blacklist`  (
  `file` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `hash` varchar(256) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `detail` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `time` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
