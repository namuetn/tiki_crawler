from bs4 import BeautifulSoup
import re

html = '''
    <div class="ToggleContent__View-sc-1dbmfaw-0 wyACs" style=""><p><span style="font-weight:400"><strong>[PHIÊN BẢN CẢI TIẾN MỚI]</strong> Kem chống nắng giúp bảo vệ da khỏi tia UVB &amp; UVA dài và giảm bóng nhờn La Roche-Posay Anthelios UV Mune 400 Oil Control Gel-Cream 50ml</span></p>
<p><strong>THÔNG TIN SẢN PHẨM</strong></p>
<p><strong>*Loại sản phẩm</strong><br><span style="font-weight:400">- Kem chống nắng dành cho da dầu giúp kiểm soát dầu với độ bảo vệ cao SPF 50+.</span></p>
<p><strong>*Loại da phù hợp</strong><br><span style="font-weight:400">- Phù hợp cho da dầu và da hỗn hợp.</span><span style="font-weight:400"><br></span><span style="font-weight:400">- Sử dụng cho da mặt.</span></p>
<p><strong>*Độ an toàn</strong><br><span style="font-weight:400">- Được kiểm nghiệm dưới sự giám sát của các chuyên gia da liễu.</span><span style="font-weight:400"><br></span><span style="font-weight:400">- Không chứa hương liệu, không paraben, không gây bết dính, không để lại vệt trắng, lâu trôi khi sử dụng dưới nước và không gây mụn trứng cá.</span><span style="font-weight:400"><br></span><span style="font-weight:400">- Tuyệt đối an toàn với da, đặc biệt là da nhạy cảm.</span></p>
<p><strong>*Thành phần</strong><br><span style="font-weight:400">- Màng lọc độc quyền MEXORYL 400: Màng lọc UV duy nhất trên thị trường và hiệu quả nhất, kể cả trước những tia UVA dài làm hủy hoại tế bào da với bước sóng 380-400nm. Ngăn chặn hiểu quả của thâm nám da.</span><span style="font-weight:400"><br></span><span style="font-weight:400">- Hoạt chất AIRLICIUM: Với 99% không khí và 1% silica, hợp chất này có khả năng kháng mồ hôi vượt trội, tạo ra một lớp finish lì và giảm thiểu bã nhờn.</span></p>
<p><strong>*Ưu điểm nổi bật</strong><br><span style="font-weight:400">- Kết cấu dạng kem gel, thẩm thấu tức thì, mang lại cảm giác khô thoáng, không để lại vệt trắng.</span><span style="font-weight:400"><br></span><span style="font-weight:400">- Kiểm soát bã nhờn &amp; mồ hôi giúp mang đến một cảm giác “sạch” cho làn da đến 9h.</span><span style="font-weight:400"><br></span><span style="font-weight:400">- Bảo vệ da trước những tác hại từ ánh nắng &amp; ô nhiễm: lão hóa sớm, đốm nâu, kích ứng ánh nắng.</span><span style="font-weight:400"><br></span><span style="font-weight:400">- Độ chống nắng cao nhất SPF 50+ bảo vệ da tối ưu dưới ánh nắng.</span></p>
<p><strong>*Hiệu quả sử dụng:</strong></p>
<p><span style="font-weight:400">-25% bóng dầu sau 1 tuầng<br>&gt; 83% tạo hiệu ứng lì 12h trên da<br>&gt; 97% không gây nhờn rít, bết dính sau 12h sử dụng<br>&gt; 98% không để lại vệt trắng trên da</span></p>
<p><strong>*Hướng dẫn sử dụng:</strong><br><span style="font-weight:400">- Thoa kem trước khi tiếp xúc với ánh nắng 20 phút.</span><span style="font-weight:400"><br></span><span style="font-weight:400">- Lấy một lượng sản phẩm vừa đủ và chấm 5 điểm trên mặt (trán, mũi, cằm và hai bên má) sau đó thoa sản phẩm theo chiều từ trong ra ngoài và trên xuống dưới.</span></p>
<p><strong>*Hướng dẫn bảo quản</strong><br>- Nơi thoáng mát, tránh ánh nắng mặt trời trực tiếp</p>
<p><br>HSD: 3 năm kể từ NSX<br>NSX: Xem trên bao bì<br>Xuất xứ thương hiệu: Pháp<br>Nơi sản xuất: Pháp<br><strong><em>Hình ảnh sản phẩm có thể thay đổi theo từng đợt nhập</em></strong></p>
<p><br><strong>THÔNG TIN THƯƠNG HIỆU</strong></p>
<p>La Roche-Posay là nhãn hàng dược mỹ phẩm đến từ Pháp trực thuộc tập đoàn L’Oreal đã hoạt động được hơn 30 năm, phối hợp nghiên cứu với các chuyên gia da liễu trên toàn thế giới cho ra đời các sản phẩm dưỡng da hướng đến thị trường sản phẩm dành cho da nhạy cảm, ngoài ra còn có dòng sản phẩm dành cho trẻ em. Thành phần nổi bật xuất hiện trong các sản phẩm của La Roche-Posay (LRP) là nước suối khoáng – thermal spring water. Tất cả những sản phẩm thuộc La Roche Posay đều được thử nghiệm lâm sàng và đánh giá khách quan từ viện Saint Jacques-Toulouse. Quy trình bào chế của sản phẩm cũng rất nghiêm ngặt mang lại cho người sử dụng vẻ đẹp tự nhiên và rất an toàn.</p><p>Giá sản phẩm trên Tiki đã bao gồm thuế theo luật hiện hành. Bên cạnh đó, tuỳ vào loại sản phẩm, hình thức và địa chỉ giao hàng mà có thể phát sinh thêm chi phí khác như phí vận chuyển, phụ phí hàng cồng kềnh, thuế nhập khẩu (đối với đơn hàng giao từ nước ngoài có giá trị trên 1 triệu đồng).....</p></div>
'''

soup = BeautifulSoup(html, 'html.parser')
pattern = re.compile(r'thành phần', re.IGNORECASE)
# elements = soup.find('strong', text='*Thành phần')
elements = soup.find_all(string=pattern)
# elements = soup.find_all('p', string=lambda text: text and '*Thành phần' in text)
print(elements)

# print(result)