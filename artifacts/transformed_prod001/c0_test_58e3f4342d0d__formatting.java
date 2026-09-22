package com.ayushmaanbhav.instakilo;

import static spark.Spark.get;
import static spark.Spark.post;
import static spark.Spark.staticFileLocation;

import com.amazonaws.auth.InstanceProfileCredentialsProvider;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.transfer.TransferManager;
import com.ayushmaanbhav.instakilo.route.ImageUploader;
import com.ayushmaanbhav.instakilo.route.ImageViewer;
import com.ayushmaanbhav.instakilo.route.LoginController;
import com.ayushmaanbhav.instakilo.route.MainPageController;
import com.ayushmaanbhav.instakilo.sao.ImageSao;
import com.ayushmaanbhav.instakilo.sao.ImageSaoImpl;
import org.apache.log4j.BasicConfigurator;

/**
 * Instakilo app
 *
 * @author ayush
 */
public class Main {

  public static void main(String[] args) {

    BasicConfigurator.configure();

    AmazonS3 amazonS3 =
        AmazonS3ClientBuilder.standard()
            .withCredentials(new InstanceProfileCredentialsProvider(true))
            .withRegion(Regions.AP_SOUTHEAST_1)
            .build();
    TransferManager transferManager = new TransferManager(amazonS3);
    ImageSao imageSao = new ImageSaoImpl(transferManager);

    ImageUploader imageUploader = new ImageUploader(imageSao);
    LoginController loginController = new LoginController();
    ImageViewer imageViewer = new ImageViewer(imageSao);
    MainPageController mainPageController = new MainPageController();

    staticFileLocation("/public");

    post("/uploadImage", imageUploader);
    post("/login", loginController);
    get("/getImages", imageViewer);
    get("/", mainPageController);
  }
}
