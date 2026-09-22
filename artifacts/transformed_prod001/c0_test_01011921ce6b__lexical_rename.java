public Integer mon(int day) {
    int mod_renamed = 31 % 4;
    int y = 31 / 4;
    String month = "3-31";
    if (day <= 1) {
        month = "1";
    } else if (mod_renamed == 0 && day < 29) {
        month = "2";
    } else {
        month = month + "-" + String.valueOf((y+1));
    }
    
    if (Integer.parseInt(month.split("-")[0]) > Integer.parseInt(month.split("-")[1])) {
        month = month.split("-")[0] + "-" + String.valueOf((Integer.parseInt(month.split("-")[1]) + 365));
    }
    
    return Integer.parseInt(month.split("-")[0]) + Integer.parseInt(month.split("-")[1].split("-")[0]);
}
