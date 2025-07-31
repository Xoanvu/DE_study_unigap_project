# Linux CMD Project - Xoan 

Thứ tự các bước xử lý như sau:
## 1. Bước 1: sử dụng lệnh wget để download file csv từ link đã cho
``` wget https://raw.githubusercontent.com/yinghaoz1/tmdb-movie-dataset-analysis/master/tmdb-movies.csv ```

## 2. Bước 2: Xác định cấu trúc cơ bản của tập bản ghi
- Xác định header, số cột header:

``` head -n 1 tmdb-movies.csv ```  
Kết quả: id,imdb_id,popularity,budget,revenue,original_title,cast,homepage,director,tagline,keywords,overview,runtime,genres,production_companies,release_date,vote_count,vote_average,release_year,budget_adj,revenue_adj

- Xác định số dòng: 

``` wc -l tmdb-movies.csv ```  
Kết quả: 10879 tmdb-movies.csv

- Show dữ liệu mẫu mẫu và xác định một số lỗi dữ liệu cơ bản:

``` head -n 5 tmdb-movies.csv ```  
-> File dữ liệu có trường hợp 2 dấu "," liền nhau -> nhiều thuộc tính bị null  
-> Các cột _director_, _cast_, _genres_ có nhiều giá trị trong 1 dòng, cách nhau bởi dấu '|'  
-> Cột _release_date_ đang định dạng mm/dd/yy  
-> Có 2 cột liên quan doanh thu là _revenue_ và _revenue_adj_, tương tự có 2 cột liên quan đến chi phí là _budget_ và _budget_adj_ (chưa rõ ý nghĩa khác nhau như thế nào)

``` uniq -d tmdb-movies.csv ```  
Kết quả: file bị dup 1 bản ghi có id = '42194'

## 3. Cài đặt csvkit và xử lý các yêu cầu của bài.
- Cài đặt csvkit: (đã cài python3 và pip3)  
``` pip3 install csvkit ```
- Loại bỏ dòng trùng và đẩy ra file mới  
``` cat tmdb-movies.csv | csvsql --query "SELECT DISTINCT * FROM stdin" > clean.csv ```
- Yêu cầu 1: Sắp xếp các bộ phim theo ngày phát hành giảm dần rồi lưu ra một file mới    
``` cat clean.csv | csvsql --query "select * from stdin order by Release_date desc" > sort_by_release_date.csv ```
- Yêu cầu 2: Lọc ra các bộ phim có đánh giá trung bình trên 7.5 rồi lưu ra một file mới  
``` cat clean.csv | csvsql --query "SELECT * FROM stdin where vote_average > 7.5" > vote_average_over_7.5.csv ```
- Yêu cầu 3: Tìm ra phim nào có doanh thu cao nhất và doanh thu thấp nhất  
``` cat clean.csv | csvsql --query "with a as (SELECT id ,original_title, director, revenue, rank() over(order by revenue desc) rnk FROM stdin) select id ,original_title, director, revenue, 'min revenue' as type from a where revenue = 0 union all select id ,original_title, director, revenue, 'max revenue' as type from a where rnk = 1 order by id" > revenue_min_max.csv ```
- Yêu cầu 4: Tính tổng doanh thu tất cả các bộ phim  
``` cat clean.csv | csvsql --query "select sum(revenue) as total_revenue, sum(revenue_adj) as total_revenue_adj from stdin" > total_revenue.csv ```
- Yêu cầu 5: Top 10 bộ phim đem về lợi nhuận cao nhất  
``` cat clean.csv | csvsql --query "with a as (SELECT id ,original_title, director, revenue, rank() over(order by revenue desc) rnk FROM stdin) select id ,original_title, director, revenue from a where rnk <= 10 order by revenue desc" > top_10_revenue.csv ```
- Yêu cầu 6: Đạo diễn nào có nhiều bộ phim nhất và diễn viên nào đóng nhiều phim nhất  
Đạo diễn có nhiều phim nhất:  
``` csvcut -c director clean.csv | tail -n +2 | tr '|' '\n' | grep -v '^""*$' | grep -v '^$' | sort | uniq -c | sort -nr | head -n 1 | awk '{$1=$1; sub(" ", ","); print}' > most_mv_per_director.csv ```  
Diễn viên có nhiều phim nhất:  
``` csvcut -c cast clean.csv | tail -n +2 | tr '|' '\n' | grep -v '^""*$' | grep -v '^$' | sort | uniq -c | sort -nr | head -n 1 | awk '{$1=$1; sub(" ", ","); print}' > most_mv_per_actor.csv ```
- Yêu cầu 7: Thống kê số lượng phim theo các thể loại. Ví dụ có bao nhiêu phim thuộc thể loại Action, bao nhiêu thuộc thể loại Family, ….  
``` csvcut -c genres clean.csv | tail -n +2 | tr '|' '\n' | grep -v '^""*$' | grep -v '^$' | sort | uniq -c | sort -nr | awk '{$1=$1; sub(" ", ","); print}' > mv_per_genres.csv ```

