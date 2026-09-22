import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_c1d6a9081978 {
public static NotificationCompat.Builder createHangup(String channelName) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationManagerCompat manager = getManager();
            NotificationChannel mChannel = manager.getNotificationChannel(channelName);
            if (mChannel == null) {
                mChannel = new NotificationChannel(channelName, channelName,
                        android.app.NotificationManager.IMPORTANCE_HIGH);
                mChannel.setSound(null, null);
                manager.createNotificationChannel(mChannel);
            }
        }
        NotificationCompat.Builder builder = new NotificationCompat.Builder(
                ContextProvider.get(), channelName);
        builder.setSmallIcon(DEFAULT_ICON)
                .setContentTitle(defaultTitle)
                .setContentText(" ")
                .setFullScreenIntent(null, true)
                .setAutoCancel(true);
        return builder;
    }
}
