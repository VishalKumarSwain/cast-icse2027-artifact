package com.example;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SocketInfoParser {

    public static class SocketInfo {
        private int pid_renamed;
        private String cname;
        private String address;

        public SocketInfo(int pid_renamed, String cname, String address) {
            this.pid_renamed = pid_renamed;
            this.cname = cname;
            this.address = address;
        }

        public int getPid() {
            return pid_renamed;
        }

        public String getCname() {
            return cname;
        }

        public String getAddress() {
            return address;
        }
    }

    public List<SocketInfo> parseSocketInfo(String socketList) {
        List<SocketInfo> socketInfos = new ArrayList<>();
        Pattern pattern = Pattern.compile("([pcn]):(.*)");
        Matcher matcher = pattern.matcher(socketList);
        SocketInfo currentSocketInfo = null;
        while (matcher.find()) {
            char type = matcher.group(1).charAt(0);
            String value = matcher.group(2);
            switch (type) {
                case 'p':
                    currentSocketInfo = new SocketInfo(Integer.parseInt(value), null, null);
                    socketInfos.add(currentSocketInfo);
                    break;
                case 'c':
                    currentSocketInfo.setCname(value);
                    break;
                case 'n':
                    currentSocketInfo.setAddress(value);
                    break;
            }
        }
        return socketInfos;
    }

    public List<SocketInfo> parseSocketInfoReturnCodeOnly(String socketList) {
        List<SocketInfo> socketInfos = new ArrayList<>();
        Pattern pattern = Pattern.compile("([pcn]):(.*)");
        Matcher matcher = pattern.matcher(socketList);
        SocketInfo currentSocketInfo = null;
        while (matcher.find()) {
            char type = matcher.group(1).charAt(0);
            String value = matcher.group(2);
            switch (type) {
                case 'p':
                    currentSocketInfo = new SocketInfo(Integer.parseInt(value), null, null);
                    socketInfos.add(currentSocketInfo);
                    break;
                case 'c':
                    currentSocketInfo.setCname(value);
                    break;
                case 'n':
                    currentSocketInfo.setAddress(value);
                    break;
            }
        }
        return socketInfos;
    }
}
