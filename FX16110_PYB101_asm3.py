import urllib.request, urllib.parse, urllib.error
import json
import xml.etree.ElementTree as et

def tax_rate(salary):       # tính thuế suất với từng mức thu nhập
    tax_file = urllib.request.urlopen('https://firebasestorage.googleapis.com/v0/b/funix-way.appspot.com/o/xSeries%2FChung%20chi%20dieu%20kien%2FPYB101x_1.1%2FASM_Resources%2Ftax.xml?alt=media&token=f7a6f73d-9e6d-4807-bb14-efc6875442c7').read()
    tax_data = et.fromstring(tax_file)
    taxes = tax_data.findall('tax')
    for tax in taxes:
        mini = int(tax.find('min').text)
        try:
            maxi = int(tax.find('max').text)
        except:
            maxi = float('inf')
        value = int(tax.find('value').text)
        if salary/1000000 >= mini and salary/1000000 < maxi:
            return 0.01 * value
        else:
            continue
     
def late_penalty(late_comming_days):        # tính số tiền tổng nộp phạt
    penalty_file = urllib.request.urlopen('https://firebasestorage.googleapis.com/v0/b/funix-way.appspot.com/o/xSeries%2FChung%20chi%20dieu%20kien%2FPYB101x_1.1%2FASM_Resources%2Flate_coming.json?alt=media&token=55246ee9-44fa-4642-aca2-dde101d705de').read()
    penalty_data = json.loads(penalty_file)
    for penalty in penalty_data:
        mi = penalty.get('min')
        try:
            ma = penalty.get('max')
        except:
            ma = float('inf')
        val = penalty.get('value')
        if late_comming_days >= mi and late_comming_days < ma:
            return late_comming_days * val
        else:
            continue


class Employee:     # nhân viên
    cv = 'NV'
    
    def __init__(self, id, name, salary_base, working_days, department, working_performance, bonus, late_comming_days):
        self.id = id
        self.name = name
        self.salary_base = int(salary_base)
        self.working_days = int(working_days)
        self.department = department
        self.working_performance = float(working_performance)
        self.bonus = int(bonus)
        self.late_comming_days = int(late_comming_days)

    @property
    def tinh_luong(self):
        no_bonus_salary = self.salary_base * self.working_days * self.working_performance
        penalty = late_penalty(self.late_comming_days)
        salary = no_bonus_salary + self.bonus + Department(self.department, department_dict[self.department]).bonus_salary - penalty
        return int((salary * 0.895) - salary * tax_rate(salary*0.895) * 0.895)
        
        
class Manager(Employee):        # quản lý
    cv = 'QL'
    
    def __init__(self, id, name, salary_base, working_days, department, working_performance, bonus, late_comming_days):
        super().__init__(id, name, salary_base, working_days, department, working_performance, bonus, late_comming_days)

    @property
    def tinh_luong(self):
        no_bonus_salary = self.salary_base * self.working_days * self.working_performance
        penalty = late_penalty(self.late_comming_days)
        salary = no_bonus_salary + self.bonus + Department(self.department, department_dict[self.department]).bonus_salary * 1.1 - penalty
        return int((salary * 0.895) - salary * tax_rate(salary*0.895) * 0.895)        
    

class Department:       # bộ phận
    def __init__(self, id, bonus_salary):
        self.id = id
        self.bonus_salary = bonus_salary
 

def format_money(a):        # hàm chuẩn hoá số liệu dạng tiền
    if len(str(a)) < 7:
        return str(a)[:-3] + ',' + str(a)[-3:]
    elif len(str(a)) < 10:
        return str(a)[:-6] + ',' + str(a)[-6:-3] + ',' + str(a)[-3:]


department_dict = {}        # dict sẽ có dạng {"tên bộ phận": thưởng bộ phận}
nv_data = {'nv':[]}         # dict sẽ có dạng {'nv':[list thông tin của tất cả nhân viên, mỗi item là dict riêng 1 nv]}
id_list = []                # list id tất cả nhân viên
department_list = []        # list id các bộ phận

def update():               # load file JSON dữ liệu các nhân viên lên để điền vào các list, dict ở trên; khi này các list, dict này phải trống y hệt như trên
    try:
        nv_file = open('nv_data.json')  # tên file dữ liệu nv. Nội dung file sẽ có format giống dictionary nv_data
        nv_data_cu = json.load(nv_file)
        nv_data_moi = nv_data_cu.get('nv')
        for d in nv_data_moi:
            if d['id'] not in id_list:
                nv_data['nv'].append(d)
                id_list.append(d['id'])
            if d['department'] not in department_list:
                department_list.append(d['department'])
                department_dict[d['department']] = int(d['bonus_salary'])
        nv_file.close()
    except:
        pass


while True:         # tạo menu khi khởi động, khi chưa có dữ liệu nv nào thì nên chọn số 3 để điền nv đầu tiên
    menu = input('''1. Hiển thị danh sách nhân viên.
2. Hiển thị danh sách bộ phận.
3. Thêm nhân viên mới.
4. Xóa nhân viên theo ID.
5. Xóa bộ phân theo ID
6. Hiển thị bảng lương.
7. Thoát.
Mời bạn nhập chức năng mong muốn (VD: 1 ):''')

    if menu == '1':
        update()        # điền vào các dict, list đã tạo ở trên: bước này là để cập nhật dữ liệu mới nhất từ file
        for i in nv_data['nv']:
            print('''----
Mã số: {0}
Mã bộ phận: {1}
Chức vụ: {2}
Họ và tên: {3}
Hệ số lương: {4} (VND)
Số ngày làm việc: {5} (ngày)
Hệ số hiệu quả: {6}
Thưởng: {7} (VND)
Số ngày đi muộn: {8}
----'''.format(i['id'], i['department'], i['cv'], i['name'], format_money(i['salary_base']), i['working_days'], i['working_performance'], format_money(i['bonus']), i['late_comming_days']))

    elif menu == '2':
        update()
        for d in department_list:
            print('''----
Mã bộ phận: {0}
Thưởng bộ phận: {1} (VND)
----'''.format(d, format_money(department_dict[d])))

    elif menu == '3':
        update()
        print('''----
Thêm nhân viên mới ...''')
        def them_nv(txt):       # hàm xử lý sơ bộ input
            while True:
                x = input(txt)
                if x != '':
                    if x[-1:].isnumeric() == True and float(x) < 0:
                        print('''Bạn phải nhập một số dương
----''')
                    else:
                        return x
                else:
                    print('''Bạn không được bỏ trống thông tin này
----''')
        id = them_nv('Nhập mã số:')         # lấy input và điền vào các dict, list đã update
        if id in id_list:
            print('''Mã nhân viên đã tồn tại
----''')
            continue
        department = them_nv('Nhập mã bộ phận:')
        if department not in department_list:
            bs = int(them_nv('''Mã bộ phận chưa tồn tại, tạo mới ...
Nhập thưởng bộ phận:'''))
            department_dict[department] = bs
            print('''Đã tạo bộ phận mới ...''')
        cv = them_nv('Nhập chức vụ (NV / QL):')
        name = them_nv('Nhập họ và tên:')
        salary_base = them_nv('Nhập hệ sô lương:')          
        working_days = them_nv('Nhập số ngày làm việc:')
        working_performance = them_nv('Nhập hệ số hiệu quả:')
        bonus = them_nv('Nhập thưởng:')
        late_comming_days = them_nv('Nhập số ngày đi muộn:')
        if cv == 'NV':
            nv = Employee(id, name, salary_base, working_days, department, working_performance, bonus, late_comming_days)
        elif cv == 'QL':
            nv = Manager(id, name, salary_base, working_days, department, working_performance, bonus, late_comming_days)
        de = Department(department, department_dict[department])
        nv_data['nv'].append({'id':nv.id, 'name':nv.name, 'salary_base':nv.salary_base, 'working_days':nv.working_days, 'department':nv.department, 'working_performance':nv.working_performance, 'bonus':nv.bonus, 'late_comming_days':nv.late_comming_days, 'cv':nv.cv, 'bonus_salary':de.bonus_salary})
        nv_file1 = open('nv_data.json','w')
        json.dump(nv_data, nv_file1)        # sử dụng các dict, list đã update ghi đè dữ liệu mới vào file
        nv_file1.close()
        nv_data = {'nv':[]}         # sau khi ghi xong đặt lại các dict, list để tránh trùng lặp, sai sót khi chọn chức năng khác
        id_list = []
        department_list = []
        department_dict = {}
        print('''Đã thêm nhân viên mới ...
----''')

    elif menu == '4':
        update()
        y = input('''----
Nhập mã nhân viên muốn xóa:''')
        if y not in id_list:
            print('''Mã nhân viên không tồn tại
----''')
        else:
            for i in nv_data['nv']:
                if i['id'] == y:
                    nv_data['nv'].remove(i)                    
            nv_file = open('nv_data.json','w')
            json.dump(nv_data, nv_file)         # tương tự như chức năng 3, chỉ khác là xoá
            nv_file.close()
            nv_data = {'nv':[]}
            id_list = []
            department_list = []
            department_dict = {}
            print('''Đã xóa thành công
----''')

    elif menu == '5':
        update()
        z = input('''----
Nhập mã bộ phận muốn xóa:''')
        if z in department_list:
            print('''Bạn không thể xóa bộ phận đang có nhân viên
----''')
        else:
            print('''Đã xóa thành công
----''')

    elif menu == '6':
        update()
        for i in nv_data['nv']:
            if i['cv'] == 'NV':
                nv = Employee(i['id'], i['name'], i['salary_base'], i['working_days'], i['department'], i['working_performance'], i['bonus'], i['late_comming_days'])
                bp = Department(i['department'], i['bonus_salary'])
                print('''----
Mã số: {}
Thu nhập thực nhận: {} (VND)
----'''.format(nv.id, format_money(nv.tinh_luong)))
            else:
                nv = Manager(i['id'], i['name'], i['salary_base'], i['working_days'], i['department'], i['working_performance'], i['bonus'], i['late_comming_days'])
                bp = Department(i['department'], i['bonus_salary'])
                print('''----
Mã số: {}
Thu nhập thực nhận: {} (VND)
----'''.format(nv.id, format_money(nv.tinh_luong)))

    elif menu == '7':
        break

    elif menu == '8':
        update()
        def sua_nv(txt):        # gần giống hàm them_nv, ở đây là sửa
            while True:
                x = input(txt)
                if x != '':
                    if x[-1:].isnumeric() == True and float(x) < 0:
                        print('''Bạn cần nhập đúng định dạng
----''')
                    else:
                        return x
                else:
                    return 'khong doi'
        id = sua_nv('''----
Chỉnh sửa nhân viên
Nhập mã nhân viên:''')
        if id not in id_list:
            print('''Nhân viên không tồn tại
----''')
            continue
        else:
            for i in nv_data['nv']:     # lấy ra các giá trị cũ 
                if i['id'] == id:
                    name0 = i['name']
                    department0 = i['department']
                    cv0 = i['cv']
                    salary_base0 = i['salary_base']
                    working_days0 = i['working_days']
                    working_performance0 = i['working_performance']
                    bonus0 = i['bonus']
                    late_comming_days0 = i['late_comming_days']
                    bs0 = i['bonus_salary']
                    nv_data['nv'].remove(i)     # xoá các giá trị cũ của nhân viên được sửa trên dictionary nv_data giống chức năng xoá
        def choose(x, txt):     # hàm trả về giá trị cũ nếu input trống
            y = sua_nv(txt)
            if y == 'khong doi':
                return x
            else:
                return y
        department = choose(department0, 'Nhập mã bộ phận:')
        if department not in department_list:
            bs = int(choose(bs0, '''Mã bộ phận chưa tồn tại, tạo mới ...
Nhập thưởng bộ phận:'''))
            department_dict[department] = bs
            print('''Đã tạo bộ phận mới ...''')
        cv = choose(cv0, 'Nhập chức vụ (NV / QL):')
        name = choose(name0, 'Nhập họ và tên:')
        salary_base = choose(salary_base0, 'Nhập hệ sô lương:')          
        working_days = choose(working_days0, 'Nhập số ngày làm việc:')
        working_performance = choose(working_performance0, 'Nhập hệ số hiệu quả:')
        bonus = choose(bonus0, 'Nhập thưởng:')
        late_comming_days = choose(late_comming_days0, 'Nhập số ngày đi muộn:')
        if cv == 'NV':
            nv = Employee(id, name, salary_base, working_days, department, working_performance, bonus, late_comming_days)
        elif cv == 'QL':
            nv = Manager(id, name, salary_base, working_days, department, working_performance, bonus, late_comming_days)
        de = Department(department, department_dict[department])
        nv_data['nv'].append({'id':nv.id, 'name':nv.name, 'salary_base':nv.salary_base, 'working_days':nv.working_days, 'department':nv.department, 'working_performance':nv.working_performance, 'bonus':nv.bonus, 'late_comming_days':nv.late_comming_days, 'cv':nv.cv, 'bonus_salary':de.bonus_salary})
        nv_file1 = open('nv_data.json','w')
        json.dump(nv_data, nv_file1)        # sử dụng các dict, list đã update ghi đè dữ liệu mới vào file
        nv_file1.close()
        nv_data = {'nv':[]}         # sau khi ghi xong đặt lại các dict, list để tránh trùng lặp, sai sót khi chọn chức năng khác
        id_list = []
        department_list = []
        department_dict = {}
        print('''Đã hoàn tất chỉnh sửa
----''')

    else:
        print('''Chức năng không tồn tại
----''')
