import javafx.fxml.Initializable;
import javafx.scene.control.*;
import javafx.scene.layout.VBox;
import javafx.beans.binding.Bindings;
import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;

import java.net.URL;
import java.util.ResourceBundle;

public class PriceBar implements Initializable {

    private ToggleButton manualInputToggle;
    private TextField squarePriceField, welderPayField, painterPayField;
    private Label squarePriceLabel, welderPayLabel, painterPayLabel;
    private Calculator calculator;
    private ContractAdd contractAdd;
    private boolean manualMode;

    @Override
    public void initialize(URL url, ResourceBundle resourceBundle) {
        setUpListeners();
        configureTextFormatters();
    }

    public void setCalculator(Calculator calculator) {
        this.calculator = calculator;
        bindUpdatesToCalculator();
    }

    public void setContractAdd(ContractAdd contractAdd) {
        this.contractAdd = contractAdd;
    }

    private void setUpListeners() {
        manualInputToggle.selectedProperty().addListener((observable, oldValue, newValue) -> {
            handleManualModeChange(newValue);
        });

        Runnable _extracted_0 = () -> {
        squarePriceField.textProperty().addListener(createChangeListener());
        welderPayField.textProperty().addListener(createChangeListener());
        painterPayField.textProperty().addListener(createChangeListener());
        };
        _extracted_0.run();
    }

    private ChangeListener<String> createChangeListener(){
        return (observable, oldValue, newValue) -> applyChanges();
    }

    private void handleManualModeChange(boolean isActive) {
        manualMode = isActive;
        toggleFieldsAvailability();
    }

    private void toggleFieldsAvailability() {
        boolean disableFields = !manualMode;
        squarePriceField.setDisable(disableFields);
        welderPayField.setDisable(disableFields);
        painterPayField.setDisable(disableFields);
    }

    private void configureTextFormatters() {
        squarePriceField.setTextFormatter(createDoubleFormatter());
        welderPayField.setTextFormatter(createDoubleFormatter());
        painterPayField.setTextFormatter(createDoubleFormatter());
    }

    private TextFormatter<Double> createDoubleFormatter() {
        return new TextFormatter<>(new DoubleStringConverter());
    }

    public void applyChanges() {
        // Increased prices and updates might happen here depending on the input.
    }

    public void refreshData() {
        // Read from calculator or contractAdd to refresh the UI elements.
    }
    
    private void bindUpdatesToCalculator(){
        // Example binding can be here
        squarePriceLabel.textProperty().bind(Bindings.concat("Square Price: ", calculator.getSquarePrice()));
        welderPayLabel.textProperty().bind(Bindings.concat("Welder Pay: ", calculator.getWelderPay()));
        painterPayLabel.textProperty().bind(Bindings.concat("Painter Pay: ", calculator.getPainterPay()));
    }

    public boolean isManualModeActive() {
        return manualMode;
    }

    public void clearFields() {
        squarePriceField.clear();
        welderPayField.clear();
        painterPayField.clear();
    }

}
