# Đối chiếu triển khai và phạm vi xác minh

## Nguồn mã và spec

- Fork: `Arashi0881/MinesweeperAI`, nhánh làm việc `solver`.
- Nền thuật toán đã đối chiếu: `fbd7711b669b5476ff4114e0bb11eaf47184ac45`.
- Phần spec đã triển khai nằm ở `0c1622a64d7b43f094e33c91e0decaae778498e3`
  trên nhánh `solver`, không phải `main` của fork.
- Bản spec người dùng cung cấp được lưu nguyên nội dung tại
  `Spec_tai_lap_thuc_nghiem_Minesweeper.md`.
- Không tìm thấy bộ CSV/manifest đầy đủ trong checkout hoặc lịch sử nhánh
  được chọn; bảng trong báo cáo và bộ 200 ván của HEURISTICS.md không thay thế
  dữ liệu từng ván của ma trận này.

Các constructor `opening_strategy`, tùy chọn `include_outside`, solver factory
của `run_game`, ba script và README đã có. Không triển khai lại chúng và không
sửa các tệp trong `minesweeper/` ở đợt này.

## Các thiếu sót đã sửa trong quy trình

1. Một cấu hình có thể thuộc nhiều nhóm nhưng cần cỡ mẫu khác nhau. CSV dùng
   cỡ mẫu lớn nhất; `group_games` và `group_summary.csv` giữ cỡ mẫu riêng. Điểm
   mật độ 10 mìn dùng seed 0–499, không dùng cả baseline 0–999.
2. Kiểm tra manifest schema, ma trận cấu hình, cấu hình từng dòng CSV,
   seed/count/result, độ hữu hạn của time_ms và các bất biến coverage.
3. Bổ sung SHA-256 của CSV, snapshot mã Python và kiểm tra snapshot. Patch Git
   giữ chỉnh sửa tệp tracked; snapshot giữ cả mã Python untracked liên quan.
4. Biểu đồ từ chối ô dữ liệu bị thiếu thay vì vẽ cột 0; bổ sung hatch,
   thông tin luật chơi/cỡ mẫu và thứ tự preset theo kích thước.
5. Đồng bộ uv.lock với extra matplotlib đã được nhánh solver khai báo.
6. Thêm coverage mô tả từ các trường CSV sẵn có và đủ thống kê thời gian vào
   các bảng Markdown.

Manifest của benchmark ghi nền commit và patch vì code chưa được commit mới.
Khi tái lập chính xác đợt đo, dùng cả commit, working_tree.patch và
source_snapshot.zip; chỉ checkout commit nền không bao gồm các sửa script.
Snapshot lúc chạy và script tạo đầu ra về sau có thể được đối chiếu bằng
checksum trong các tệp provenance.

## Xác minh quy trình

- Trên nền fbd7711: 208 passed, 3 skipped vì thiếu màn hình.
- Trên nhánh solver trước sửa script: 212 passed, 3 skipped.
- Sau thêm kiểm thử quy trình: 224 passed, 3 skipped.
- Smoke all: 43 cấu hình × 5 ván = 215 dòng, sinh được bảng, PNG 300 DPI và SVG.
- Smoke main lần hai: 16 cấu hình × 5 ván = 80 dòng. Mọi trường ngoài time_ms
  trùng lần một, gồm result, moves, guesses và cells_revealed.
- Chạy script từ thư mục khác bằng đường dẫn tuyệt đối được xác minh.
- Các kiểm thử âm xác nhận từ chối dữ liệu bị cắt, cấu hình/seed/result/time
  sai và nhóm biểu đồ thiếu. Không ghi đè thư mục đã có kết quả.

Kết quả benchmark đầy đủ và đối chiếu báo cáo được ghi trong thư mục
`data/full_20261011` và audit của bản báo cáo cập nhật. Smoke không được trộn
với dữ liệu chính thức.

## Những đánh giá còn lại

| Vấn đề | Trạng thái và bước đánh giá phù hợp |
|---|---|
| Degree Heuristic, propagation, INFO | Chưa có ablation; giữ cùng frontier và tập nghiệm để đo riêng chi phí DFS, tách khỏi thí nghiệm đổi cách chọn nước. Không suy ra đóng góp riêng từ tỉ lệ thắng. |
| Node, prune, độ sâu, thời gian DFS | Chưa có DFSStats. time_ms hiện là toàn ván, không đo riêng DFS hay từng nước; bỏ số đo riêng DFS lịch sử khỏi phần kết quả mới. |
| Brute-force độc lập | Chưa triển khai bộ đối chiếu rộng. Bước tiếp theo nên liệt kê mọi vector nhị phân cho component nhỏ và cả bố trí toàn cục với tổng số mìn, đối chiếu tập nghiệm và Fraction; không dùng chính hàm xác suất của solver làm oracle. |
| Safe Cell Coverage | Đã tính trực tiếp từ CSV, gồm trung bình mọi ván và riêng stalled. Đây là thống kê mô tả, không phải kết luận nhân quả hoặc nghiệm tối ưu. |
| Chênh lệch biến thể | Chưa kiểm định trong spec. Outside có thể đối chiếu theo seed trên cùng bàn bằng McNemar; center/corner hoặc đổi luật click đầu có thể thay đổi bố trí, không gọi là cùng bàn chỉ vì trùng seed. |
| LV3 | Mặc định chỉ chọn frontier khi có xác suất; không có timeout/cache, DFS lưu toàn bộ nghiệm. include_outside là biến thể đã có, không đổi mặc định. |
| Thông tin mâu thuẫn | Solver giả định cờ đúng, có thể bỏ ràng buộc bất hợp lệ hoặc fallback; benchmark không chứng minh xử lý được mọi cờ sai. |
| GUI | Ba kiểm thử cần màn hình vẫn skipped. Cancel bỏ chờ/kết quả, không dừng tính toán worker. Chưa kiểm tra chuột/DPI/hiển thị dài trên nhiều hệ điều hành. |
| Báo cáo Word | Kiểm tra nội dung/bảng/hình bằng cấu trúc DOCX; máy không có bộ dàn trang Word. Cần cập nhật mục lục/số trang khi mở trong Word, không khẳng định bản mới vẫn đúng 25 trang. |

Quy trình thí nghiệm được xác minh không đồng nghĩa thuật toán đã được chứng
minh đúng bằng brute-force hoặc giao diện đã được kiểm tra đầy đủ.
