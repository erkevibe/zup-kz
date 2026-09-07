package kz.zup;

import lsfusion.base.file.FileData;
import lsfusion.base.file.RawFileData;
import lsfusion.server.data.sql.exception.SQLHandledException;
import lsfusion.server.language.ScriptingErrorLog;
import lsfusion.server.language.ScriptingLogicsModule;
import lsfusion.server.logics.action.controller.context.ExecutionContext;
import lsfusion.server.logics.classes.ValueClass;
import lsfusion.server.logics.property.classes.ClassPropertyInterface;
import lsfusion.server.physics.dev.integration.internal.to.InternalAction;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.ss.util.CellRangeAddress;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.Map;

/** Presentation only: the source XLSX is already filtered by role and organization. */
public class FormatEnforcementXlsxAction extends InternalAction {
    public FormatEnforcementXlsxAction(ScriptingLogicsModule module, ValueClass... classes) {
        super(module, classes);
    }

    @Override
    public void executeInternal(ExecutionContext<ClassPropertyInterface> context)
            throws SQLException, SQLHandledException {
        FileData source = (FileData) context.getKeyValue(getOrderInterfaces().get(0)).getValue();
        try {
            findProperty("System.exportFile[]").change(
                    new FileData(new RawFileData(format(source.getRawFile().getBytes())), "xlsx"), context);
        } catch (IOException | ScriptingErrorLog.SemanticErrorException e) {
            throw new IllegalStateException("Не удалось оформить Excel-выгрузку", e);
        }
    }

    public static byte[] format(byte[] source) throws IOException {
        try (XSSFWorkbook book = new XSSFWorkbook(new ByteArrayInputStream(source));
             ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            Sheet sheet = book.getSheetAt(0);
            book.setSheetName(0, "Данные");
            Row header = sheet.getRow(0);
            int columns = header.getLastCellNum();
            Font font = book.createFont();
            font.setFontName("Arial");
            font.setFontHeightInPoints((short) 10);
            Font headerFont = book.createFont();
            headerFont.setFontName("Arial");
            headerFont.setFontHeightInPoints((short) 10);
            headerFont.setBold(true);
            headerFont.setColor(IndexedColors.WHITE.getIndex());
            CellStyle heading = book.createCellStyle();
            heading.setFont(headerFont);
            heading.setFillForegroundColor(IndexedColors.DARK_BLUE.getIndex());
            heading.setFillPattern(FillPatternType.SOLID_FOREGROUND);
            heading.setAlignment(HorizontalAlignment.CENTER);
            heading.setVerticalAlignment(VerticalAlignment.CENTER);
            heading.setWrapText(true);
            header.setHeightInPoints(32);
            for (Cell cell : header) cell.setCellStyle(heading);

            // Reuse styles; never allocate a style for every row or alter cell values/types.
            Map<String, CellStyle> styles = new HashMap<>();
            for (Row row : sheet) {
                if (row.getRowNum() == 0) continue;
                for (Cell cell : row) {
                    String format = cell.getCellStyle().getDataFormatString();
                    if (cell.getCellType() == CellType.STRING) format = "@";
                    else if (header.getCell(cell.getColumnIndex()).getStringCellValue().endsWith("KZT"))
                        format = "#,##0.00";
                    else if (DateUtil.isCellDateFormatted(cell))
                        format = format.toLowerCase().contains("h") ? "dd.mm.yyyy hh:mm:ss" : "dd.mm.yyyy";
                    String key = cell.getCellStyle().getIndex() + ":" + format;
                    CellStyle style = styles.get(key);
                    if (style == null) {
                        style = book.createCellStyle();
                        style.cloneStyleFrom(cell.getCellStyle());
                        style.setFont(font);
                        style.setDataFormat(book.createDataFormat().getFormat(format));
                        style.setVerticalAlignment(VerticalAlignment.TOP);
                        style.setWrapText(true);
                        styles.put(key, style);
                    }
                    cell.setCellStyle(style);
                }
            }
            for (int col = 0; col < columns; col++) {
                sheet.autoSizeColumn(col);
                sheet.setColumnWidth(col, Math.max(16 * 256, Math.min(64 * 256, sheet.getColumnWidth(col) + 512)));
            }
            for (Row row : sheet) {
                if (row.getRowNum() == 0) continue;
                int lines = 1;
                for (Cell cell : row) if (cell.getCellType() == CellType.STRING) {
                    int capacity = Math.max(1, (int) (sheet.getColumnWidth(cell.getColumnIndex()) / 256.0 * 0.8));
                    int count = 0;
                    for (String part : cell.getStringCellValue().split("\\R", -1))
                        count += Math.max(1, (part.length() + capacity - 1) / capacity);
                    lines = Math.max(lines, count);
                }
                // ponytail: conservative wrapped-text height; extreme fonts need editor autofit.
                row.setHeightInPoints(Math.min(409, Math.max(22, lines * 14 + 4)));
            }
            sheet.createFreezePane(0, 1);
            sheet.setAutoFilter(new CellRangeAddress(0, sheet.getLastRowNum(), 0, columns - 1));
            sheet.setDisplayGridlines(false);
            book.write(out);
            return out.toByteArray();
        }
    }
}
