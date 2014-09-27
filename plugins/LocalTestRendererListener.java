import java.awt.*;

import model.*;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;


public final class LocalTestRendererListener {
    public void afterDrawScene(Graphics graphics, World world, Game game, double scale) {
    }

    public void beforeDrawScene(Graphics graphics, World world, Game game, double scale) {

        try {
            File file = new File("draw");
            if (!file.exists()) {
                return;
            }
            FileReader fileReader = new FileReader(file);
            BufferedReader bufferedReader = new BufferedReader(fileReader);
            String line;
            while ((line = bufferedReader.readLine()) != null) {
                String[] parts = line.split("\\s+");
                if (parts[0].equals("circle")) {
                    int x = (int) (Double.parseDouble(parts[1]) * scale);
                    int y = (int) (Double.parseDouble(parts[2]) * scale);
                    int radius = (int) (Double.parseDouble(parts[3]) * scale);
                    graphics.drawArc(x - radius, y - radius, 2 * radius, 2 * radius, 0, 360);
                } else if (parts[0].equals("line")){
                    int x1 = (int) (Double.parseDouble(parts[1]) * scale);
                    int y1 = (int) (Double.parseDouble(parts[2]) * scale);
                    int x2 = (int) (Double.parseDouble(parts[3]) * scale);
                    int y2 = (int) (Double.parseDouble(parts[4]) * scale);
                    graphics.drawLine(x1, y1, x2, y2);
                } else if (parts[0].equals("point")){
                    int x = (int) (Double.parseDouble(parts[1]) * scale);
                    int y = (int) (Double.parseDouble(parts[2]) * scale);
                    int radius = 1;
                    graphics.drawArc(x - radius, y - radius, 2 * radius, 2 * radius, 0, 360);
                } else {
                    System.out.println(line);
                    System.out.println(parts[0]);
                }
            }
            fileReader.close();
            file.delete();
        } catch (IOException e) {
        }
    }
}
