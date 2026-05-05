# Reflection — Lab 19

**Tên:** NGUYỄN VĂN LĨNH
**Mã HV:** 2A202600412
**Cohort:** A20-K1
**Path đã chạy:** lite

---

## Câu hỏi (≤ 200 chữ)

> Trên golden set 50 queries, mode nào thắng ở loại query nào (`exact` /
> `paraphrase` / `mixed`), và tại sao? Khi nào bạn **không** dùng hybrid
> (i.e. khi nào pure BM25 hoặc pure vector là lựa chọn đúng)?

- **Truy vấn exact:** BM25 (từ khóa) thường cho điểm cao nhất; hybrid chỉ tương đương hoặc hơi tốt hơn vì các từ khóa đã được BM25 nắm bắt.
- **Truy vấn paraphrase:** Vector (ngữ nghĩa) thắng vì câu hỏi được diễn đạt lại và không có các từ khóa xuất hiện nguyên văn; BM25 giảm mạnh, hybrid chỉ đạt mức tương đương vector.
- **Truy vấn mixed:** Hybrid (BM25 + Vector + RRF) thắng rõ rệt, kết hợp lợi thế của cả khớp từ khóa và tương đồng ngữ nghĩa.

**Khi nào không nên dùng hybrid**

- Nếu mọi truy vấn đều exact và corpus đã được lập chỉ mục tốt, pure BM25 đủ và nhanh hơn.
- Nếu mô hình embedding không phù hợp với ngôn ngữ (ví dụ: model tiếng Anh trên dữ liệu tiếng Việt) và độ recall ngữ nghĩa thấp, nên dùng pure BM25.
- Trong môi trường tài nguyên hạn chế, chạy cả hai chỉ mục tăng độ trễ; chọn phương pháp phù hợp với loại truy vấn chiếm đa số (BM25 cho workload nhiều exact, vector cho workload nhiều paraphrase).

---

## Điều ngạc nhiên nhất khi làm lab này

- Thấy được sức mạnh của hybrid search: chỉ với một công thức RRF đơn giản, độ chính xác trung bình tăng đáng kể so với pure BM25 hay pure vector, và cách thức kết hợp thực tế phản ánh đúng nhu cầu production.

---

## Bonus challenge

- [x] Đã làm bonus (xem `bonus/`)
- [x] Pair work với: Phạm Lê Hoàng Nam
