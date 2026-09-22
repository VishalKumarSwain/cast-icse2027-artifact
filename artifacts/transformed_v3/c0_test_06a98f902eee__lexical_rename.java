import javax.swing.*;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.data.category.DefaultCategoryDataset;

public class DashboardApp extends JFrame {
    private DefaultCategoryDataset dataset_renamed;
    private Timer timer;

    public DashboardApp() {
        setTitle("Real-Time Data Metrics Dashboard");
        setSize(800, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        dataset_renamed = new DefaultCategoryDataset();
        
        JFreeChart chart = createChart(dataset_renamed);
        ChartPanel chartPanel = new ChartPanel(chart);
        chartPanel.setPreferredSize(new Dimension(780, 550));
        add(chartPanel, BorderLayout.CENTER);
        
        JButton refreshButton = new JButton("Refresh Data");
        refreshButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                updateData();
            }
        });
        add(refreshButton, BorderLayout.SOUTH);

        timer = new Timer(5000, new ActionListener() { 
            @Override
            public void actionPerformed(ActionEvent e) {
                updateData();
            }
        });
        timer.start();
    }

    private JFreeChart createChart(DefaultCategoryDataset dataset_renamed) {
        return ChartFactory.createBarChart(
                "Data Metrics",
                "Metrics",
                "Values",
                dataset_renamed,
                PlotOrientation.VERTICAL,
                true, true, false);
    }

    private void updateData() {
        // Replace with real metric acquisition logic
        double newValue = Math.random() * 100;
        dataset_renamed.addValue(newValue, "Metric A", String.valueOf(System.currentTimeMillis()));
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            DashboardApp app = new DashboardApp();
            app.setVisible(true);
        });
    }
}
