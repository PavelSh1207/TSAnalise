package org.example;

import ec.tstoolkit.algorithm.CompositeResults;
import ec.tstoolkit.algorithm.IProcessing;
import org.jfree.chart.ChartUtils;
import tech.tablesaw.api.*;
import tech.tablesaw.columns.Column;
import tech.tablesaw.io.csv.CsvReadOptions;

import ec.satoolkit.tramoseats.TramoSeatsSpecification;

import ec.tss.sa.processors.TramoSeatsProcessor;

import ec.tstoolkit.algorithm.ProcessingContext;

import ec.tstoolkit.timeseries.simplets.TsData;
import ec.tstoolkit.timeseries.simplets.TsPeriod;
import  ec.tstoolkit.timeseries.simplets.TsFrequency;

import java.io.IOException;
import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.data.category.DefaultCategoryDataset;

import java.io.File;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import javax.swing.JFrame;

class InitDataSet {

    //init class start properties
    private static final String BASE_PATH = System.getProperty("user.dir") + File.separator;
    public String filePath;
    public Table df;

    public InitDataSet(String fileName) {

        //init function parameters
        this.filePath = BASE_PATH + fileName;

        //core
        try {
            this.df = Table.read().csv(CsvReadOptions.builder(this.filePath).build());
        } catch (Exception e) {

            String message = "File was not found in current path -> " + this.filePath;
            System.out.println(message);
            e.printStackTrace();

        }
    }

    public void logs(){

        //log
        String message = "Data set from <" + this.filePath + ">: was succesfully read: file -> \n" + this.df;
        System.out.println(message);

    }
}

class TramoModel{

    private final TramoSeatsSpecification spec = new TramoSeatsSpecification();
    private final TramoSeatsProcessor processor = new TramoSeatsProcessor();
    private final ProcessingContext context = ProcessingContext.getActiveContext();
    private final String[] messageIDs = {"s", "sa", "t", "i"};
    private final String[] messages = {"Season component", "Original timeseries without season component component is\n", "Trend component is\n", "Residuals is\n:"};
    public CompositeResults result;
    public String columnName, log;

    //the class waiting of argument source file name
    // start year observation
    // start mont observation
    public TramoModel(String fileName, int year, int month, int colIndex){

        //init dataSet
        InitDataSet dataSet = new InitDataSet(fileName);

        //init model perioud
        TsPeriod start = new TsPeriod(TsFrequency.Monthly, year, month);

        //init model data
        double[] columnDouble = ((DoubleColumn) dataSet.df.column(colIndex)).asDoubleArray();
        List columnNames = dataSet.df.columnNames();
        this.columnName = (String) columnNames.get(colIndex);

        TsData tsData = new TsData(start, columnDouble, false);

        //model processing
        IProcessing<TsData, CompositeResults> processing = processor.generateProcessing(spec, context);
        this.result = processing.process(tsData);

    }

    public void logs(){

        //log
        String message = "\nResults for col <" + this.columnName + ">\n\n";



        for (int i = 0; i < 3; i++){

            String mes = "->" + this.messages[i] + this.result.getData(this.messageIDs[i], TsData.class) + "\n";
            message += mes;

        }

        System.out.println(message);
    }
}

class Plot extends JFrame{

    public DefaultCategoryDataset dataset = new DefaultCategoryDataset();
    public String titleName;
    public JFreeChart chart;
    public ChartPanel chartPanel;
    public HashMap<String, String> titleNames = new HashMap<>();


    public Plot(CompositeResults results, String type, String col){

        TsData plotData = results.getData(type, TsData.class);

        titleNames.put("s", "Season component");
        titleNames.put("t", "Trend");
        titleNames.put("sa", "Original timeseries withou season component");
        titleNames.put("i", "Residuals");

        this.titleName = titleNames.get(type) + "_col_is_" + col;



        for (int i = 0; i < plotData.getLength(); i++){

            this.dataset.addValue(plotData.get(i), "Series1", plotData.getStart().plus(i).toString());

        }

        this.chart = ChartFactory.createBarChart(

                this.titleName,
                "Date",
                "Value",
                this.dataset,
                PlotOrientation.VERTICAL,
                false,
                true,
                false

        ); //plot title and properties description

        this.chartPanel = new ChartPanel(this.chart); //locate plot on panel

        this.chartPanel.setPreferredSize(new java.awt.Dimension(800, 600));// set plot prefer size
        setContentPane(this.chartPanel);

    }

    public void savePlotPNG(){

        String fileName  = this.titleName + ".png";
        int width = this.chartPanel.getWidth();
        int height = this.chartPanel.getHeight();

        File file = new File(fileName);

        try {

            ChartUtils.saveChartAsPNG(file, this.chart, width, height);
            System.out.println("chart was saved");

        } catch (IOException e) {

            System.out.println("Error! Chart was not saved!");
            e.printStackTrace();

        }
    }
}


public class Main {

    public static void main(String[] args){

        String file = "mainDataSet.csv";

        InitDataSet dataSet = new InitDataSet(file);
        dataSet.logs();

        String[] modelIDs = {"s", "sa", "t", "i"};
        int len = dataSet.df.columnNames().toArray(new String[0]).length;

        for (int i = 1; i < len; i++) {

            TramoModel model = new TramoModel(file, 2010, 0, i);
            model.logs();

            for (String modelID : modelIDs) {
                Plot myPlot = new Plot(model.result, modelID, model.columnName);
                myPlot.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
                myPlot.pack();
                myPlot.setLocationRelativeTo(null);
                myPlot.setVisible(true);
                myPlot.savePlotPNG();
            }
        }
    }
}

