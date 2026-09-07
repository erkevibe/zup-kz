import kz.zup.FormatEnforcementXlsxAction;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import java.io.*;
import java.nio.file.*;

/** Run with -ea against the assembled server jar; no database or new test dependency. */
public class FormatEnforcementXlsxTest {
    static void verify(byte[] before, byte[] after) throws Exception {
        try (XSSFWorkbook a = new XSSFWorkbook(new ByteArrayInputStream(before));
             XSSFWorkbook b = new XSSFWorkbook(new ByteArrayInputStream(after))) {
            Sheet source = a.getSheetAt(0), target = b.getSheetAt(0);
            assert a.getNumberOfSheets() == b.getNumberOfSheets();
            assert source.getLastRowNum() == target.getLastRowNum();
            assert target.getPaneInformation().getHorizontalSplitPosition() == 1;
            assert b.getSheetAt(0).getCTWorksheet().isSetAutoFilter();
            for (Row row : source) {
                Row styled = target.getRow(row.getRowNum());
                assert row.getLastCellNum() == styled.getLastCellNum();
                for (Cell cell : row) {
                    Cell actual = styled.getCell(cell.getColumnIndex());
                    assert cell.getCellType() == actual.getCellType() : cell.getAddress();
                    if (cell.getCellType() == CellType.NUMERIC)
                        assert cell.getNumericCellValue() == actual.getNumericCellValue() : cell.getAddress();
                    else assert cell.toString().equals(actual.toString()) : cell.getAddress();
                    if (cell.getCellType() == CellType.STRING && row.getRowNum() > 0)
                        assert actual.getCellStyle().getDataFormatString().equals("@");
                    assert target.getColumnWidth(cell.getColumnIndex()) >= 16 * 256;
                    assert target.getColumnWidth(cell.getColumnIndex()) <= 64 * 256;
                }
            }
            assert b.getFontAt(target.getRow(0).getCell(0).getCellStyle().getFontIndex()).getBold();
        }
    }

    public static void main(String[] args) throws Exception {
        if (!FormatEnforcementXlsxTest.class.desiredAssertionStatus())
            throw new IllegalStateException("Run with java -ea");
        byte[] source = Files.readAllBytes(Path.of(args[0]));
        byte[] result = FormatEnforcementXlsxAction.format(source);
        verify(source, result);
        Files.write(Path.of(args[1]), result);
        try (XSSFWorkbook edge = new XSSFWorkbook(); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            Sheet sheet = edge.createSheet();
            Row header = sheet.createRow(0);
            String[] labels = {"ИИН", "Основание", "Дата", "Сумма, KZT"};
            for (int i = 0; i < labels.length; i++) header.createCell(i).setCellValue(labels[i]);
            // Empty export still has a usable header and no invented data rows.
            edge.write(out);
            verify(out.toByteArray(), FormatEnforcementXlsxAction.format(out.toByteArray()));
            Row row = sheet.createRow(1);
            row.createCell(0).setCellValue("001234567890");
            row.createCell(1).setCellValue("=НЕ_ФОРМУЛА\n" + "Қазақша текст; ".repeat(35));
            Cell date = row.createCell(2);
            date.setCellValue(46000);
            CellStyle dateStyle = edge.createCellStyle();
            dateStyle.setDataFormat(edge.createDataFormat().getFormat("dd.mm.yyyy"));
            date.setCellStyle(dateStyle);
            row.createCell(3).setCellValue(0.0);
            sheet.createRow(2).createCell(3).setCellValue(-1234.56);
            out.reset();
            edge.write(out);
            verify(out.toByteArray(), FormatEnforcementXlsxAction.format(out.toByteArray()));
        }
        System.out.println("PASS: XLSX values/types preserved; headers, widths, filters, empty/long/zero/negative cases");
    }
}
