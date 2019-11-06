#coding:utf-8

"""
@author: zhushisheng
@version: 3.3.2

PS：config:直接运行后生成一个配置文件,配置数据库相关的配置
    log:脚本当前路径的log文件夹中，以数据库_操作方式_时间_log来命名

1.0.0：添加mysql的增删改单独操作，自定义sql语句执行模式，增删改连续操作
2.0.0：添加sqlserver的增删改单独操作，自定义sql语句执行模式，增删改连续操作
3.0.0：添加oracle的增删改单独操作，自定义sql语句执行模式，增删改连续操作
3.0.1：修复linux下日志输出的问题
3.0.2：修复sqlserver,oracle-update时无返回值报错（无返回值，但是去获取值所以报错）
3.1.1：增加mysql增删改的性能测试功能，计算平均值
3.1.2：修复mysql 插入和更新自定义大字段类型报错，更新的数据无法显示
3.1.3：修改配置生成为gbk编码，读取的编码也为gbk
3.1.4：修复mysql获取字段也加入指定数据库名称导致获取到其他库相同的字段名导致插入失败
3.1.5: 修复sqlserver 插入自定义大字段类型报错
3.1.6: 修复oracle 插入自定义大字段类型报错
3.1.7: 修复sqlserver表字段和数据类型查找sql不够精确导致sql拼接错误
3.1.8: 添加mysql 多线程插入的方式
3.1.9：修改mysql commit提交方式为小循环一次的数据提交一次，之前是每条数据提交一次导致服务器压力大，也可以提高插入效率
3.2.0：修改sqlserver commit提交方式为小循环一次的数据提交一次 修复sqlserver起始插入失败的问题
3.2.1：修改oracle commit提交方式为小循环一次的数据提交一次 修复oracle起始插入失败的问题
3.2.2：修复mysql 起始值插入的问题，修复log日志后缀名去除分钟和秒，修改单个文件大小为800K
3.3.2：添加外部指定配置文件运行，若不存在指定配置文件或错误文件则使用默认配置文件运行，修改日志文件大小为20MB,
       使用配置文件名+时间生成日志名称
       修改custom语句若为更新则日志名为update，若为删除日志名则为delete
"""

import pymysql,pymssql,time,uuid,random,binascii,threading,os,logging,sys
from logging.handlers import RotatingFileHandler
import cx_Oracle as pyoracle
from threading import  Thread


class LogSignleton(object):
    def __init__(self):
        pass

    def __new__(cls):
        if not os.path.exists(os.getcwd()+'%slog'%os.sep):
            os.makedirs(os.getcwd()+'%slog'%os.sep)
        config = Config()
        database_type = config.read_config('database_type')
        try:
            test_mode = config.config_path
            log_path = os.getcwd()+'%slog%s%s_%s_log.txt'%(os.sep,os.sep,test_mode,time.strftime("%Y-%m-%d-%H",time.localtime()))

        except:
            test_mode = config.read_config('test_mode')
            if test_mode == 'custom':
                custom_sql = config.read_config('custom_sql')
                if 'UPDATE' in custom_sql.upper():
                    test_mode = 'update'
                if 'DELETE' in custom_sql.upper():
                    test_mode = 'delete'
            log_path = os.getcwd()+'%slog%s%s_%s_%s_log.txt'%(os.sep,os.sep,database_type,test_mode,time.strftime("%Y-%m-%d-%H",time.localtime()))
        with open(log_path,'a') as f:
            f.write('')
        mutex=threading.Lock()
        mutex.acquire()
        if not hasattr(cls, 'instance'):
            cls.instance = super(LogSignleton, cls).__new__(cls)
            cls.instance.log_filename = log_path#log文件位置
            cls.instance.max_bytes_each = 20048000 #单个文件大小
            cls.instance.backup_count = 1000 #同一时刻可存留的日志数量
            cls.instance.fmt = '%(asctime)s  %(levelname)s %(lineno)d %(message)s' #日志格式
            cls.instance.log_level_in_console = 10 #日志级别：CRITICAL = 50 ERROR = 40 WARNING = 30 INFO = 20 DEBUG = 10 NOTSET = 0
            cls.instance.log_level_in_logfile = 20 #日志级别：CRITICAL = 50 ERROR = 40 WARNING = 30 INFO = 20 DEBUG = 10 NOTSET = 0
            cls.instance.logger_name = 'zss' #用户名
            cls.instance.console_log_on = 1 #控制台输出开关
            cls.instance.logfile_log_on = 1 #日志输出开关
            cls.instance.logger = logging.getLogger(cls.instance.logger_name)
            cls.instance.__config_logger()
        mutex.release()
        return cls.instance

    def get_logger(self):
        return  self.logger

    def __config_logger(self):
        # 设置日志格式
        formatter = logging.Formatter(self.instance.fmt)

        if self.console_log_on == 1: # 如果开启控制台日志
            console = logging.StreamHandler()
            console.setFormatter(formatter)
            self.logger.addHandler(console)
            self.logger.setLevel(self.log_level_in_console)

        if self.logfile_log_on == 1: # 如果开启文件日志
            rt_file_handler = RotatingFileHandler(self.log_filename, maxBytes=self.max_bytes_each, backupCount=self.backup_count)
            rt_file_handler.setFormatter(formatter)
            self.logger.addHandler(rt_file_handler)
            self.logger.setLevel(self.log_level_in_logfile)

class Config():
    def __init__(self):
        try:
            self.config_path = sys.argv[1]
            if not os.path.isfile(sys.argv[1]):
                print('ERROR：%s 配置文件不存在!!!   使用默认配置文件'%sys.argv[1])
                self.config_path = 'config.ini'
            else:
                self.config_path = sys.argv[1]
        except:
            self.config_path = 'config.ini'

        if not os.path.exists('config.ini'):
            with open('config.ini','a',encoding='gbk') as f:
                f.write('全局配置：\n')
                f.write('数据库类型\n')
                f.write('database_type-->mysql\n\n')

                f.write('数据库ip\n')
                f.write('ip-->192.168.3.11\n')
                f.write('数据库端口\n')
                f.write('port-->3306\n')
                f.write('数据库账号\n')
                f.write('username-->zss\n')
                f.write('数据库密码\n')
                f.write('password-->zss\n')
                f.write('数据库名(Oracle填写实例名)\n')
                f.write('db_name-->test\n')
                f.write('数据库表名\n')
                f.write('table_name-->mysqltest1\n\n')
                f.write('SQL语句显示开关，1:开启显示所有SQL语句，0:不显示所有SQL语句\n')
                f.write('sql_log-->1\n\n')
                f.write('测试模式：insert/update/delete\nmode_iud(先插(数据量)再更(数据量)后删(数据量)/custom(自定义语句)\npt_insert/pt_update/pt_delete(性能测试，总数据量除以临时表总数变为0的时间=条/每秒)\n')
                f.write('test_mode-->mode_iud\n\n')
                f.write('数据量：0为无限，插入,删除,更新的条数(填写整数类型)\n')
                f.write('data_number-->50\n\n')
                f.write('操作延时：0为不延时，默认为0.2秒(填写浮点或整数)\n')
                f.write('time_sleep-->0.2\n\n')
                f.write('失败跳过延时：0为不延时，默认为5秒(填写浮点或整数)\n')
                f.write('error_sleep-->5\n\n')

                f.write('独立配置：\n')
                f.write('insert_for 循环次数\n')
                f.write('insert_for-->5\n')
                f.write('insert_for_time 循环间隔时间\n')
                f.write('insert_for_time-->5\n')

                f.write('insert_thread 线程数：默认为1  线程数量建议不超过50  每个线程插入的数据为10000  延时修改为0 则总数据为50W\n')
                f.write('insert_thread-->1\n\n')
                f.write('insert_int数据定义：add为自增 其他值为固定值(填写整型数值或者add)\n')
                f.write('insert_int_data-->add\n\n')
                f.write('insert_int_start插入数据时自增初始值：默认为1 (填写整型数值或者add)\n')
                f.write('insert_int_start-->1\n\n')
                f.write('insert_float数据定义：固定值(填写浮点数值)\n')
                f.write('insert_float_data-->1.2345678\n\n')
                f.write('insert_varchar数据定义：random_uuid为随机 其他值为固定值(填写字符或者数字)\n')
                f.write('insert_varchar_data-->random_uuid\n\n')
                f.write('insert_time数据定义：now为插入的时间 其他值为固定值(填写sql语句插入时正确的格式)\n')
                f.write('insert_time_data-->now\n\n')
                f.write('insert_blob数据定义：default为插入时随机取一种格式文件，文件包含png,txt,jpg 其他值为文件路径，建议文件较小(填写文件路径：E:\dd\cc\kk.txt  /home/ccc/kk.png)\n')
                f.write('insert_blob_data-->default\n\n')
                f.write('uprate_int数据定义：0为不更新，设置10000000意思为原始值加10000000(填写整型数值或者0)\n')
                f.write('update_int_data-->0\n\n')
                f.write('update_int_start更新时主键的自增初始值：默认为1 (填写整型数值或者add)\n')
                f.write('update_int_start-->1\n\n')
                f.write('update_float数据定义：0为不更新，更新成固定值(填写浮点数值)\n')
                f.write('update_float_data-->9.87654321\n\n')
                f.write('update_varchar数据定义：0为不更新，random_uuid为更新成随机uuid 其他值为固定值(填写字符或者数字)\n')
                f.write('update_varchar_data-->radom_uuid\n\n')
                f.write('update_time数据定义：0为不更新，now为更新成更新数据的时间 其他值为固定值(填写sql语句插入时正确的格式)\n')
                f.write('update_time_data-->now\n\n')
                f.write('update_blob数据定义：0为不更新，default为更新时随机取一种格式文件，文件包含png,txt,jpg 自定义文件为路径(填写文件路径：E:\dd\cc\kk.txt  /home/ccc/kk.png)\n')
                f.write('update_blob_data-->default\n\n')

                f.write('mode_iud_number：间隔次数  0为无限次(填写整型数值)\n')
                f.write('mode_iud_number-->0\n\n')
                f.write('mode_iud_number：增删改操作的间隔时间 默认为5秒(填写浮点或整数)\n')
                f.write('mode_iud_sleep_time-->5\n\n')

                f.write('custom_sql：自定义更新语句(正确的sql语句)\n')
                f.write('custom_sql-->select version()\n\n')
                f.write('custom_time_sleep：操作间隔时间 默认为5秒(填写浮点或整数)\n')
                f.write('custom_time_sleep-->5\n\n')

    def read_config(self,name):
        with open(self.config_path,'r',encoding='gbk') as f:
            data = f.readlines()
            for i in data:
                i = i.strip().split('-->')
                if name == i[0]:
                    return i[1]

class DataBase_test():
    def __init__(self):
        try :
            self.payload_list = ['0x89504e470d0a1a0a0000000d4948445200000054000000590806000000a0f5031f000000017352474200aece1ce90000000467414d410000b18f0bfc6105000000097048597300000ec300000ec301c76fa8640000136e49444154785eed5c09784d67febeed4c7535c568e9a86e0c3a6847dbe9a69db64651d452cadf566d09424210894842a48910b18444edbba8d82242958c22928a7d5f1241364b4223482c21effffd7d3977dca6e7e6de9bdca825eff3fc9ee49e7bee39df79bfdffa2dc79093938332b19f94116a672923d4ce5246a89da58c503b4b19a176960782d0ab57afe2c68d1b4af4beb7a7941aa1b9b9b9c8cbcbc3cd9b3771fdfa75dd73ee84483bf2f3f391b47123d8185cbb764df73c7b49a9112a449edbb50b737bf4500f22e4ea9d672af2f022a61aa527f2bdf15cbdeb988ab4e3e4a64d68673060db9429eab3de79f6925221541ef416091c59b72e3af3417cebd7072e5ffe0da9a6c4c9f15bb76e4170252303e9478fe2525212ce6edf8e33f1f148ddb205e9b1b138b36d9b3a7efae041649d3eadee21bf93df8b8825c8358df7509dba7b377a3ffc303cdf790723ead4016f68554714574a8550212969fd7a383df6184e9288b19f7d8641d5abe33249303ebc9861ceb97338121585ada1a198dbad9b7a60cf175ec0e0679f45ff4a9530f0af7f85fb33cfc0edf9e7e15ea50a5c2b57c6001e1b44f1e079c36bd54268f3e6583f7c38f62e5c880c122d102245b249bec3238fe0072727e45eba8401152be2c0ca95eafe7aedb687940aa142d6acf6ed11dab2a57a40d1a4f17cf041d5aae1fce1c3d8b7681126366a843ee5caa10f491f5eaf1ee6f5ea85f5132762efaa5548dbbb1717cf9cc1950b1770ede2455ca5765fcbce466e56963a9e4ae28e444763d3d4a908777141d0279fa03f4976e4b50692f8b0be7db17fe95278b01317393bab360816f1b8a76829515a5a6a7742a5a137f8d7ed6f7fc3aef070d578c1e5cc4cf47af24974a20be857a10282dbb543dc9225f83525453ba36490607392ee61ddd8b1f8eebdf7f00dcdfc1bde6be7b265da1940666a2abee5b194989852d352bb132a7eecf87fff8bc13449c18d2b57b0cad7179e6fbc8171ad5a61eb8205b8483f59da389b908068ba92800f3fc4b0f7df47c4a851c8a3bf5d408d1dcf63cae5e8b4bfa46277422548ccfffa6bcc7774c49ec848b8bff412fcfffd6f1ca44ffd4340e2b6b31d7e6c83f7abaf62999b1bfa3ef104b26919a591ced99550313bc1600612170616cfbfff1d9ba925770be266ce54a44a0a35ad6347a5a51240f59ea5b86237428d6486f7ef8f6e6cf042febdc4287eb7e11adbba2e38180e8f3f8e90366d548e6c4f52ed42a8e47e821f48621709042b56a8cf77334eeed903c7aa5511f0af7fa9cff622b5c484aa249e7e73c3b871f8f6a18770e4c71f5503adc155a64297ce9ed53e951c6759102493a81b5a075bc2b9c4443833df15f317d883d412116a24337efa7474a466ee3149518a423e7fb394c1c18d3e7660edda086adc18a7f7efd7beb51d57e85a829a36855b8d1a18d9a001bc98f0ef611e6a0dce1c3b863e4ce7a676e8a03e9b565ac59112112ad548322b2131f3d8397354832c218f9135989593071f7affba75483d74084b5c5de1c1bc35fdc001ed2ceb719929d8481606a12c242e2427ab1c78d38c19e8c10a695b58987656d138c192b63bad6b85bbbb0a542521b5d8848a795c65d5d28fbdbb7ce850ad6996b1c2cb0bde24208715902922fcfce0faca2baa1ab20591010118c7aaab30e25934383efd34d2d861d6e0d04f3fa13b15e3f8860dcaeaf49ed91a2916a1c6883e9ce61adab6adfadf5a1c6735738955931ee2e932727efd55fb641d2493c833e33363e6cd43e2ce9dda27cbd84acd964aea1ccbe3e2565236132a7e53cce2873e7dd0af7c795cb19180bb1d53e83a0655a9a2fe2fced8a9cd844acf9da05974654f1eddb449ddf87e422e4b655796cd61ddbb17ab3cb58950a3a9f7a76f5ae5edadfebf1f9172f020bea2c2a451616c357d9b0815671de5e101ef9a35718b11fe7e46c4c89170ab5c598d05d862fa5613aa925ea625e2b40f47476bb7bd7f91cfe7756325154105b225ea5b45a831104dfce413047ef49176cbfb1fbb58428be98b2259aba556112ada99b16f9fcad39298043f4818fdfefb98ddae9dd55a6a15a1a29d327733a15933ed360f0e92e2e2d0fb4f7f52458c355a6a9150751126cffd1e7d14892c331f448ca39b5be6e46495965a2454eaf5f5fefef07beb2dedf2b663cfaa55581712a24682ae6ba99739e453ce1e3b86ad336762e3a449b8cabcb030a4669709bd832c1773d9464b90fa3e61cb16ac090ac2998404eda8f5105f3aa85225dce2752cd5f94512aa82110995d9c3cd53a76a97b70d32b22423f7cde87fbfa6b8bffc32823ef800c12d5b62ee575f21ac470f2ca24885328135f9f0575f452f9ad8173c5746d64fb0542d8cd5acfb3fe57732e1e7f6e28b6ad653664d57fbfa229a9d103d7932d67cf71d1638386042d3a6f078e92535e8dd94b272c810ed2ad6e31a3bb57fc58a38b272a5c521be2209953997ccbd7bd5036624256997b71d093fff8c792c557dead5439f871f568b1f3a50da538434912f29ff4791994a37562a21243866fa74d5a179ecd8dd11114acb0417d2d3b19ce9ccc8faf5d193e7cbb5a4035a1792b614f94e3a7204efbd6cd8305c38754a5dc356487ba6b468819b16ccbe4842c5dc7ff4f4840f354c12dc9242b43533315111b33d3c1c31df7f8f8d74059b287173e7e2d0c68d6a7448e6e18dc8cec8400023edb03a75e0fcdc7308f7f2d2be21d82619cfdc41971245ed0cebd70ff37af7c6dc9e3db1c0d11111234660d7d2a548ddbfbfc48548fce2c5707ae209dca4b61665f6660915739706fbd4ae5d2c33b11756faf86052ab56b849533bc3cee847524fda3082642f5c3c7d1a4e4f3e89142a4351666f9650e985ac9414f47fea29ec5dbd5abbec9dc79241833047169c11a2e12ed5aae1e8e6cdeaf39d84d8e788ba75b181be592c578f3311b3844a2fa4304d7264ba74fee4c982abfe01486641e156ab161691d8716dda20a4756b5c67db4c21da2b6497366676ea84a96c83a44f62c17abc9925547e24cbff8652232430dc091c58b70eb10b176a9f6ee35706120964fe6fbfad1db98d3c9219dca50bce1e3fae1d293dac1d3306ae743902737ed42ca16a10994e3eb0614375813b81ed0b16a8c55ea271a69019d501cf3c8311afbda6168b9922913e6d3053b12bd9d9da91d2c34e063859fd97c5406933a1b7486830f33b49178a8444ffac2cdc4c4d45be2c6c2881368b258c6bd20401bcefe10d1b706ceb5665ea039f7e1a292c0a24b71c52b326e2e6cd43f28e1dd8c9bc50d6502d7773d3ae603b6e5db8a0da0e9996c9cbd38eea63dffaf52ac1cf6471603ba1bcf848a62ab3997c9b85904733456828f2e91ec0f40712c02c5443454192e8052e2e18f1eebb18c9ea6c5ab76eb8609203ffcc0a2a80dff93240f8bcf10622478d52d66433c4e7323ffe5fdb65c9d0f2e5e0c36b27fc1e09313170fecb5f708a9d6b33a137e97447d29416f3e17421bd2964060703cc27219594084b4275bc84901053d8f44d714372d59204a25f7e2968ab69dbe559646d81a48c3a38b96d9b223489d6613ba1d4329f575ec122fa515d481090064943a64dbb2df25934b590afbbab2016347f7e81569ab65d64fcf802b2757078d32635fd238542b14c7ed4ebaf6346e7cedae50a416a6ce9516998084df17f8d623d8d3f30d5b20899a9356aa6299922a20c3ffca0eb4ff745456170850aca05d94ca8f8a5591d3a20b87973ed7205c9ed7a36649eab2b3285c01933104b1ff733f3b31b9327df26f56e275416594c9ffe5b42e5b388f8539dd44d1037678e32f96c7688ed1a4affb471ec58786b6bd205f368fede0d1a60066b657f46d7990c0aa31b3786cf7ffe83ef6515dbecd9aa91f932a87137cfd78bf6c9727551022173d62c40961289423083c80f0b430c8fed8d8cd47e5080a58307abd1301917b09950a994d2a4527ae41164b38e15b83048c908b640d6b1f7661525c862ba34f0d96791131858402a9d77c987524a19870f17c40092789109fb64ba37df1a3510ebe080a9cc223cfef10fb83027fec5445bc77cf82196393a2a65d3e34cc42ca1d20397a9654ee5cb6387b6f9c08b954a8cb6282c76c91235c82bd8c7544926b38691d4089aff9daaac4a8ceddb5554170247b56d8b2d8c05326fe65cb9326e528b57b3a0f0634e2cb8ceac6200cd7d3735b8a8b97ab3848a484f4ce58d26b568a12eba9c2a3fa5552bf5bf29627993c5f4abb29a4e72c39fd8907b01e758d26ee033c992a298458bd4b128160f4bb4c56fb3e9da6675edaafe3f48f3970d64b967cf1639b75424a162f6c94c157ab1d77258dacda70f0df7f0503730877067674c66b573b7233339199ef487bed440e7ead511fae597da3705c8605a38a45a35a46babf7425ab6c4649e2bc15a8f2ba31449a898bd94969ecc4765f7c418069f9d1111ea067a3842f26509e10e2b17defe91d8cebadc5506ce892be7cfe3a8544d2690917d5f06e06b4cf2af322be849ed4c8c8e2ed2dc458a2454442e20fb2c65c5884bc58a3873e48876cbdf6289bbbbda7e2875f6bd0099ac1b405f299bcff4708344bad7af8f749eb7846e61d49b6faae3e686ed8c629150e3aa9199cc49650a407aab30ae646561201b7770cd1aedc8bd8178062197e79fc7c476edd430a029e499fd3efa08737af78663b972b868e59a518b848ac885e219dddda9817a03113200ed59ab163264d4e61ec3f19818b83245ca3599c73262ce575fa10d2d73a58b4b91a992a9584de8063f3ff86b6a5f18e78f1d831773d4cc1327b423f70ed2e8c2bc985fca6ee5c20867e622d3dea244e612f9c26235a13ff2e2a33ffe58bbd56f91c55462181d7c9ab6bdfa5e42dad1a3f0a269175ef32f58316c184633f7b614d94dc56a42d70d198200332bef249177a7d91cb0618fd2dd8293bb76c187559fdedea6b5c387e33bbab2bc22f2cec262bdc90704c0ff9fffd46ef57b8432010e33d99b7eaf6095bf3f420ae5a046447879c18fcf6cadff14b19ad0cd93276318f3517348614fcb2a0e5ff6761ca3e74d9d1ebf9b706ccb16b5635af6f0ef37b3535ac682c7bcf34ee998fc4126ebb2be2747c7791b216f4cf89ca4ca921adf7af5b02e2808c9c5d8cc555ac84849c1f6850bd5c633d974d19232a77b77eddbdf23f8d34f31bb7d7bfb132a11eef4be7de8cfde4cdbb347bbddef210b006422cd8d9151d6134931e0c4fc74f8bbef228ce6738c9594bc90e08e81ed39b57b3722030331a6512338688bd064cd93132bba75cc5c643252173ceefee28bd846cb1485d2e3454fac2694853d9c9f7a0adb162fd6ee681eb98c98e7580b67323f959a78ebecd998d0a60ddc593b7bb1fa98d0aa15c2870ec5566acba9f87864a7a79bddbc652d64c3982c83dcb97a3556d3df8774ec08afd75f875bedda086cdc181bc68cc1a689135509bd9e24595abc2143927d1f7b4cbd99c7d28a3b53b18a5063b534b9450b4c31e3c0ad81acd39465346bf870b31d1c30f6f3cfe14f1fe5cdfc76c4071f602c4d6c6afb2f31a7534784397c8b157d1d11396800a2bc3c10e53d0cab5d0762653f472ceed313733ab6c7f7345d59161940bfedcdebf8bcf516029a36c594ce9db1921d266f94b86266d79e25c42e5800b76ad5704b6a7976b61e2f7a6215a122a2f68756ad42af471f35bbb5b03810379149df96444d58d4b533cdf12174f69c852e1e63d1d521085dba7ba34ba74105f2b537baf6188b2eae81e83234145d4747e08b865fc0a74e2da4b334d4cb258b0b8901514c9b6c89f02256132abd94cf7c6c50850af899c1a6342053d77eafd543e7fe13d0eb3cd02b89720a7048037a1ea1c8e7d394044a3ad023ee32ba3ff3020e46d8f7850732fd2119cb7579cd910d39a888d5848a8836254645c1f1cf7f56259bad9075a121eddae138ff9a4346e2310cad590b1dda3ac1617f1e7aae3885ae1ff78043dd0ff06d8326e8e61884de8749e68fe9e854b50622e9068ac2556625676c58f77498cf27b30f5b4342d4f3eaf15094d844a8d197cea6c377ae5245bd41c12278fe21e679139a37c7b78cb2b26a395ea6698bc0b9c40404bef93a7a34f810df3c5b1b8bbb1b90b6cd8084b50604be6d40d7862dd0ebe53a887019a0fdc23cf63348f52c5f1e135ab7466c58187e4d4d55665c18e26bd73098493a252fd712581aaad3139b08159165e26c11829886f47afc71b5114022fa0d1e97b97cd96420d1fdc0dab5081b3000c319d5e57569e3192c0e4447ab170ffc42876f0d021b36c3a49606fe775b2e661ae0f8a4011b478f97532c626f7838faf2fea31b36443fa64a7dcb9553eb3cc73769821006b549cd9a613403a2335d596fa685b1325f4fd86aea46b1995011452acd6117d31e79ff9cac8cf3a8514355521ecc41650654066f8399aec4878622579b351578c8622f5918610502df6b44376140569a01c19d0cd830ad80d4095f1ab076e2dc82932c6037d3bcc155abe22ab5ed1a7d6226f3e9ddecd0c82143b09a85c82a2727c4040723392e0ed7997a89f6da12d50b4bb10815919b4ae4bfc59e3c9f90c0c01081dd34a9046aa6bcdf4ef256710f728e7480f4b8c08b79a1b584fabfdd087ba30cf825cc80cf688a835f2820d4afb1013f4db4ee951c42e8d0ead5917dfebc6a87e49422429c518cc78aab95a6526c428d22c44a43f4c4f43cf147025b085d1f3c136eaf1a90b2cf00d7ba062cec5740ae6bb5e790956addda292154dee428af87336d4f69498909b5568478812d840ac23dfd58ed94439f4a06f4ae668047bdba381af3fbbd4be65046a80e12e2f660f3ccf9885fbc0239176c4bdecb08b533ca08b533ca08b533ca08b533ca08b533ca08b533ca08b533ca08b533ca08b533ca08b533ca08b533f66884ca8657bd76d95bee38a1fe75eb62ff1d5ce19c1019099f975fc6c573e774db656fb963843e285246a85d2507ff0f57048d2056fa2b310000000049454e44ae426082','0x746573740d0a746573740d0a746573740d0a746573740d0a746573740d0a746573740d0a746573740d0a746573740d0a746573740d0a746573740d0a746573740d0a746573740d0a746573740d0a746573740d0a746573740d0a746573740d0a746573740d0a746573740d0a746573740d0a74657374','0xffd8ffe000104a46494600010101006000600000ffdb004300080606070605080707070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c2837292c30313434341f27393d38323c2e333432ffdb0043010909090c0b0c180d0d1832211c213232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232ffc20011080060005703012200021101031101ffc4001a000003010101010000000000000000000000030405020601ffc40017010101010100000000000000000000000001000203ffda000c03010002100310000001f74050739a3a847f6ab245568115b000c04d4ad343c438f88c27a2b3ac6668dc02125728df2a22cf5d1b715ae6d9e36d69cc870d04c6f9552d528d31d48b5df95f53e7b3dafd386a793d6f91cd67d1c80566f35b8df7e6f77ccf2b61f95e837676a456e8007201466e902877d2998fa8573d020057ffc40026100003010001020504030000000000000001020304001213101120222314303134212432ffda0008010100010502fbacc1113bd141a3ab9d76e779979dc3a4e7f60f457e5a7a6a7b3a3c6d42a252124e33acd51c51277954f3f213e0a784be4d1ca77cb26640dca4676e766d3e2162ba81fa70430e64fd73a18f1b5b2871b26c97a1e3be9a21952169dd9a7362d3cdfa9ccded264878fd50beaa3cb3dd903e6a7f6f43baf23048aea3e59c00abcaa3754acb5e6afc6c1e78f7ff0017ce9d17d3fea95492a2b529e3a66acf44aa3d479c9742d3366a9aedda099d73a48fa2e85e4a67a134d3b70e886539c083510591d85f47a6d106f3cc88f48cebcf20068cb10aaa117eefffc4002111000201040202030000000000000000000001110210213112130441223261ffda0008010301013f011220e23bbbeecb47554b2ce0eaf6447b3adaf90c44bd33c7a5555431fd8fd779c14aa9e8ca791dd38244e2ff00ffc4001e11000103040300000000000000000000000102031100122030102141ffda0008010201013f01db70a98e2ef305f43279d0d26e22692a0a4c8d3fffc40038100002000402080305060700000000000001020003111221411013223132515261042071233342a1b130727381f0f1345391a2c1d1e1ffda0008010100063f02fb52c770158136655d5b175cd3d3b47b39535fbd29f58fe1ff00bc46d489a3d318b249217e37a6eec3bc3c9fe5b507a65e559031c6b33b0f309a78185ac7972f2054f78f82c5a31cc9399d173b051ccc5cbb8f68a238af2cf450c6a3e03eeffd699933a7617fcfebb68b65daa3ace3f28bdeb31fa9f47b44063d94ea8e9998fce36d42b7206b0cc38936c7e5008dc74579b31f9c6c8dfc35e5ccc1b6f7b570d9dfdcc22a3eb6fde5852d862c05f758107d60cb922b46b5e6d69eb4853214b2106e52f9c5ff001bf0a74c35714a7175449fb83e9a26cae96a8f438c35578b7c6b17149842b0e479c33a52eef08a358587bcb976971ad4778a490448980b6399e621165d2e76b6a728a2efcc9ce0aaf13ec2fe70146e1a04d97ef172ea1ca0d3886f53bc44afc5589df76b1acc9e557fa7ef1293a3c38fd7ca3c3fe28fa18b9da91ae982da70272ffbe4927106fa5cb81dc624069b7aeb06f5c61c76892267842f6814a91130b258756b856b998974369d6ae312a662d33583698d4f9767894dcbea215c62378ec61a9c4db2a3998759a8d30860aa0e3841f12a499571439ecfef0b46c2a1ab0a8b8acb3731ef90f34b2a590bb518a1a57031792cefd4e6b48f692d5a9cc4500c20154a55d771a6716a8000c87db7ffc40027100100010303020603010000000000000001110021314161715181102091a1b1c130d1f0f1ffda0008010100013f21fcac3c397152e3ace47e0c477ad0a70df656fe871b3a83e2cd731821e47f8a25d35866ebfca3b7959a4cda6f0f2c769f314cce9f21b9dae93c7920f148dc4f5762a6e29756d65f06803a9051c99c4a8f9a5081cbb0ecdfc104011b234534a9cb748cf6e4db8f1bdb1fbdeeb7834a6deebb507a0f0931c183b781c10785c9c3a54896e0ff006f9a2aeb080f5a77d8eddef73bd39521278778a7aea4431fd8748a6d2f6c364e20c1b546498659e0c359c04fda4cca9566082ce1dab073e8f086f2f5a1d0954d930cbf2d4bc8913b4b54dabfafd1e0a532be92f793b558c36738a8b893db3801faa025080e48500205d7d64de6da1409b32bc11b917ef42c6c25f2d598d7140c261195fc69fef9167b67b55b0020e3c2c1608958ea3e9a0e54b368bb9583fc4d246c8c76bd38ce90effe14ca180f2b4b53a7c0544d0c1d57a06b45df04269eaeef6f5f232a5dfac609e628e8f4eb1752ded526eacf6a9150d4398e6aced011a02af60392f14084838c2c3c674f2b58c903aa4c77c77a8c626e6707ae6b590b74e290d15ab585c1d267e287c561505b09b12ed5021030bcc335804358b3d4bcf63ccb2f1a84afe950212c4970e9505d0d1314020010054bb62461099b16a0986c101f9bffda000c03010002000300000010f33df7ff00ce5ed757fcfe8e6e081becc0e24cf203b25bcf2eb9e73cffc40023110100020005030500000000000000000001001110213141f06191a15171b1d1e1ffda0008010301013f109692f050535805b444686929ab889acd1d4c322604c839c3bfa30cc01e78fa26d537e74bda23d1473f3ae7560c14a4dc3056ce70214cabbf8956055c618182530f7b7b524a13e1a46d17ae28ac96bbb8aacc7fffc4001c1101000203010101000000000000000000010011102131415171ffda0008010201013f108b2c970c99e63d973444f8977ba805823283644a24344a0d19adc769e0a2bdfd808904bdf77f6194b9444bcfffc400261001000104020104020301000000000000011100213141516181102071a191b130c1f0f1ffda0008010100013f10fe088cfb65dc47804bfaa427ab45a4c8ca08b3221b1cb72484fc25c8ec1ae38fb9bfde6a21de8d9e1be956c7ac817800cf6c5b7cc146d54934a2ccdd82e76f6cc10960b2209a48465931ee82c484cb1fab9604ca0bfb0938e8c884a5c1779b194a04a25c1995cbf440583d339081879693798905062600c7eea44b971139887e3d0f0b20488e44a63506a62255cd99391dbd0d8cbfc510be51e0f4809f064037b040b8bac5f0d6d59697fe981e8fc5c347c65fc1a4a19d0f8041f2d27e2136264819ce28dbc1f48f013a5501677e44928cd312f22f6bb501b32da40985f84cbe6d6cd02dce62e4482e92e1293abd8cdc191c04908a69a4608918efa306211c58b42d4049985d98ba282bab4a4d4d6a81086e2f11c3304e28d0dd5809515a11d180d4e35ec657201635398f2cef67d3305c7232ca1d4bcda36f9a94f50f56c633cb464cd5a4199d9082b811c8bab22e03299313390a0d695832d009a76208c03781768b4a0d8a32b94a1955c21c0e8732d492ed2ac32d4de555ed2b1b5a8662103ccf095d2a2561cf8041faf45dd0a4495d6d5c1d0f4b27cc90fd268e9c3914abf99f44bfaa10fbc811f6501a81f3115faa1a809e7419a3e857e7fb152e0d01bab00ba7825a4002382b663b416830b65f618c18d22d206f10518b5342714008a5c163850e38f794508109f42492657e1f2536b240085d9319c5444621196f0224df653caccd5510b610ac03af6c1329968012d58d077c8f1001426848470cd4ce1ca20a13cdde017553431602c31659cdc685422b8a0974f95365c158681680663a633dd203b660512ec5de2e64f7249fd4c80816591749d5062b2a08e41896e026bfe1e5d4951a441401c07153888ee80262e14c6eacc8223e007f37ffd9']
            self.oracle_payloads_list = ['7a73730d0a7a73730d0a7a73730d0a7a73730d0a7a73730d0a7a73730d0a7a7373','89504e470d0a1a0a0000000d49484452000000200000002d0806000000cfe4692a000002d7494441545885635c777dda7f860102b5518b199806ca72181875000b298a9f3f78c730ad6aebc0396069ef7e30bd6bebba8171000c48494a50cd01039e062872407b571f838e91158ad8aa35ebc16230ec131801165fb474058a78535b37e50ec00660061fdebb8d81998989e1c1c347607e57ef24307d64ff76b84369e20010909591661014146068a8ad00f3df7ff800a6d5549519f878791974b435c11804c84a8484c0e3274fc1f48245cbc0b4a0800098be75fb2e03232323c39f3f7f186edcbc4d3d07c0d2c1ba958bc0be0459849e3684840419debd7bcfa06b6c8d22ce484a65d493bb96e1e3db6f0c57ce1d23a8f6c4c9d30c4686fa0c6c6c6c28e2878e1c63b0b341388e2651000216e6a658c5912d0781012f07480a0175431986537b6e61c42f2580a43400031f5e7fa18ae5bdf9ebc94b0302a23c547100080c781a181a0e38b3ef36c399fd9092ebe2917b0c978edec32b4e0ac09b067efef8cdf0ffef7f869dcbce81f93a66f20cfbd65c04b3d50c64708a33323332b073b012e5009cb960c3ece30c67f7df21d21f98c0c85e9921301d7f76c5db2c7f70fd2583382707c302076b066e16163006b14162c4885f3ff3982887e28d0276607dae09ac56f375215527889da1a90e0c3706bce2ccc01aef1f51d6135912fa2bc8c1d95ef23204c54901781df0e4eb3706f7adbb4936f4f3efdf0c1c68b520590ef80f6a3cb011979a51f4fdfa45b45abc0e90939561d8ba6125c90eb0727067f8fdf727516a07bc2424ba32faf6fd3bc3972f5f71caf3707333707171d2ce0166d6ce04d510d35423db01c70eec64f8fbf72f4e792626f262936807b0b030839bd4381dc04c630798d9b8105443d328d8b9792dc3878f1f71caf3f292d74a22da01d2d292604c6d3078cb01762e5686c70f9e32d83879926ce8e7cf5f18780439287340668b374377ce5a86efdfbf91ec007e612e86c20981943900044aa704936c39a960c0d3c0803b80d1cac565c0c68a3fbefdca00009366dfb3c60e9a150000000049454e44ae426082','ffd8ffe000104a46494600010101006000600000ffdb004300080606070605080707070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c2837292c30313434341f27393d38323c2e333432ffdb0043010909090c0b0c180d0d1832211c213232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232ffc2001108002c002603012200021101031101ffc4001b00000202030100000000000000000000000006040501030702ffc4001801010101010100000000000000000000000302040001ffda000c0301000210031000000176c1abbc8686ed45529604df675a6351518d3eef6634482d8a4b4d9cb3293d7abd22bb227b221b0fffc4001f1000020203000203000000000000000000010302040005111214152122ffda000801010001050224f41975c562d5faf054f243ec90b8b6fcd52d9bbdba792f1eb2e1393602292a0f5ed28aeb633f42bac35feb232318c06ea43d2f97ab89bb52c37bccd858955ab62cb6d330120c7697621ae63e59ffc4001a110100020301000000000000000000000001021100031004ffda0008010301013f01c262d7365d819afcd2256e48a792d9673fffc4001e11010002020203010000000000000000000100020311101204053141ffda0008010201013f018d10df18fa8367f267f6146895fb30d9b631626cd4c5e2f4b6d78fffc4002810000103010704020300000000000000000100021103101213213141613251718122913382a1ffda0008010100063f02c8b7dad5a8e28f8ba9c693babd48cb4f11674028bdd4c00141a207ec8540230ce63cd9983e5380636e9ef2ba1a3ed566556de66499528e4c76447629ed9325b10831da6ebf135431a00e1536ee6a48fa5a9fe28a60621de06761a8c2d990048d55faae93b71648d54639f60157aabcb8f367ffc4002310010002010401040300000000000000000100112110315161914171a1b1c1d1f0ffda0008010100013f212e008a0bafa82e89776d9711eb794beda59e7d61081bb37961c55d368561e9bafa3f1a1b5ae1687105d94524d799521bc8fe4cbb099969cf10d1285adc0d2dd87a3696b1b91ed31c3a3c42190ed8e857f64feffda312494564374d824cfeec4c210500a074680910644f4949a1ca1e5276dbddd69fffda000c030100020003000000101fff0016f7cb2dc3ffc400191101000301010000000000000000000000010011211041ffda0008010301013f105a2d94c3bc6fd38414a84a10c46600573fffc4001e11000300020105000000000000000000000001113151102171a1e1f0ffda0008010201013f104ab88ac2e9c771215dbafb6664da2ceca1940b53dcf0250fffc4002210010002020103050100000000000000000111210031511041618191a1b1c1f1ffda0008010100013f108ac33529fbc6832564a7d2f157132129628c3df156f493d7da01678a666b59338e8953587eb1dacda8f805655f01908756118940d7e8d06aa591e4e961d280004f3e30038e6b129b41c1acb3005e31c5a7c61cc6cd228b2d0f6e71c6fc100490b7093b9d60d2535b282e3f72264412961af17884148e65fdcb5cf3425e5e5c81a0b982af7cbfb1881fb9063608aac4be988944f093f78f12ea148602b6375c616a350e1028e885d44a14691c0a3841eec07e722a310260e0341e0e9fffd9']
            logsignleton = LogSignleton()
            self.logger = logsignleton.get_logger()
            config = Config()
            self.database_type = config.read_config('database_type')
            self.ip = config.read_config('ip')
            self.port = config.read_config('port')
            self.username = config.read_config('username')
            self.password = config.read_config('password')
            self.db_name = config.read_config('db_name')
            self.table_name = config.read_config('table_name')
            self.test_mode = config.read_config('test_mode')
            self.data_number = config.read_config('data_number')
            self.time_sleep = config.read_config('time_sleep')
            self.error_sleep = config.read_config('error_sleep')
            self.sql_log = config.read_config('sql_log')

            self.insert_int_data = config.read_config('insert_int_data')
            self.insert_int_start = config.read_config('insert_int_start')
            self.insert_float_data = config.read_config('insert_float_data')
            self.insert_varchar_data = config.read_config('insert_varchar_data')
            self.insert_time_data = config.read_config('insert_time_data')
            self.insert_blob_data = config.read_config('insert_blob_data')

            self.update_float_data = config.read_config('update_float_data')
            self.update_int_start = config.read_config('update_int_start')
            self.update_varchar_data = config.read_config('update_varchar_data')
            self.update_time_data = config.read_config('update_time_data')
            self.update_blob_data = config.read_config('update_blob_data')
            self.update_int_data = config.read_config('update_int_data')

            self.mode_iud_number = config.read_config('mode_iud_number')
            self.mode_iud_sleep_time = config.read_config('mode_iud_sleep_time')

            self.custom_sql = config.read_config('custom_sql')
            self.custom_sleep = config.read_config('custom_time_sleep')

            self.insert_thread = config.read_config('insert_thread')
            self.insert_for_time = config.read_config('insert_for_time')
            self.insert_for = config.read_config('insert_for')

            if self.database_type == 'oracle':
                self.table_name = self.table_name.upper()

        except Exception as e:
            self.logger.error('获取文件配置失败，%s'%str(e))

    def mysql(self):
        # 连接mysql数据库，显示版本
        try:
            db = pymysql.connect(host=self.ip, user=self.username, passwd=self.password, db=self.db_name,
                                 port=int(self.port))
            cursor = db.cursor()
            cursor.execute('select version()')
            outinfo = cursor.fetchall()[0][0]
            self.logger.info('数据库版本:' + outinfo)
            self.logger.info('测试模式：%s' % self.test_mode)

        except Exception as e:
            self.logger.error('连接失败!!!' + str(e))

        def return_payload(path):
            with open(path, 'rb') as f:
                return '0x' + str(binascii.b2a_hex(f.read()))[2:-1]

        def get_data_type():
            # 获取表字段和数据类型来构造sql语句
            try:
                cursor.execute("""select COLUMN_NAME,DATA_TYPE from information_schema.COLUMNS where table_name = '%s' and table_schema='%s'""" % (self.table_name,self.db_name))
                tables_info = cursor.fetchall()
                tables_out_info = str(tables_info)
                self.logger.info('表字段和类型：%s ' % tables_out_info)
                return tables_info
            except Exception as e:
                self.logger.error('获取表名和字段失败!!! %s' % str(e))

        def get_tables_key():
            try:
                cursor.execute("""SELECT column_name FROM INFORMATION_SCHEMA.`KEY_COLUMN_USAGE` WHERE table_name='%s' AND CONSTRAINT_SCHEMA='%s' AND constraint_name='PRIMARY'""" % (self.table_name,self.db_name))
                tables_key_info = cursor.fetchall()[0][0]
                self.logger.info('%s数据表KEY 为：%s ' % (self.table_name,str(tables_key_info)))
                return tables_key_info
            except Exception as e:
                self.logger.error('获取%s数据表KEY失败!!! %s' % (self.table_name,str(e)))

        def make_insert_sql(index,tables_info):
            #构造insert语句
            try:
                filed_sql = ''
                data_sql = ''
                filed_sql1 = ''
                data_sql1 = ''
                tables_info = set(tables_info)

                for i in tables_info:
                    if 'int' in i[1]:
                        if self.insert_int_data != '0':
                            filed_sql = filed_sql + '`' + i[0] + '`' + ','
                            data_sql = data_sql + '%d' % index + ','
                            filed_sql1 = filed_sql1 + '`' + i[0] + '`' + ','
                            data_sql1 = data_sql1 + '%d' % index + ','
                    elif 'char' in i[1]:
                        filed_sql = filed_sql + '`' + i[0] + '`' + ','
                        filed_sql1 = filed_sql1 + '`' + i[0] + '`' + ','
                        if self.insert_varchar_data == 'random_uuid':
                            data_sql = data_sql + "'" + str(uuid.uuid1()) + '-' + str(uuid.uuid1()) + "'" + ','
                            data_sql1 = data_sql1 + "'" + str(uuid.uuid1()) + '-' + str(uuid.uuid1()) + "'" + ','
                        else:
                            data_sql = data_sql + "'" + self.insert_varchar_data + "'" + ','
                            data_sql1 = data_sql1 + "'" + self.insert_varchar_data + "'" + ','

                    elif 'float' in i[1]:
                        filed_sql = filed_sql + '`' + i[0] + '`' + ','
                        data_sql = data_sql + "'" + str(self.insert_float_data) + "'" + ','
                        filed_sql1 = filed_sql1 + '`' + i[0] + '`' + ','
                        data_sql1 = data_sql1 + "'" + str(self.insert_float_data) + "'" + ','
                    elif 'date' in i[1]:
                        filed_sql = filed_sql + '`' + i[0] + '`' + ','
                        filed_sql1 = filed_sql1 + '`' + i[0] + '`' + ','
                        if self.insert_time_data == 'now':
                            data_sql = data_sql + "'" + time.strftime("%Y-%m-%d %X") + "'" + ','
                            data_sql1 = data_sql1 + "'" + time.strftime("%Y-%m-%d %X") + "'" + ','
                        else:
                            data_sql = data_sql + "'" + self.insert_time_data + "'" + ','
                            data_sql1 = data_sql1 + "'" + self.insert_time_data + "'" + ','

                    elif 'blob' in i[1]:
                        filed_sql = filed_sql + '`' + i[0] + '`' + ','
                        filed_sql1 = filed_sql1 + '`' + i[0] + '`' + ','
                        if self.insert_blob_data == 'default':
                            data_sql = data_sql + random.choice(self.payload_list) + ','
                            data_sql1 = data_sql1 + '数据过长不显示' + ','
                        else:
                            data_sql = data_sql + return_payload(self.insert_blob_data) + ','
                            data_sql1 = data_sql1 + '数据过长不显示' + ','

                    else:
                        filed_sql = filed_sql + '`' + i[0] + '`' + ','
                        data_sql = data_sql + 'null' + ','
                sql = 'INSERT INTO `%s` ' % self.table_name + '(' + filed_sql[:-1] + ')' + ' VALUE ' + '(' + data_sql[:-1] + ")"
                out_sql = 'INSERT INTO `%s` ' % self.table_name + '(' + filed_sql1[:-1] + ')' + ' VALUE ' + '(' + data_sql1[:-1] + ")"
                if self.sql_log == '1':
                    self.logger.info('SQL:%s'%str(out_sql))
                return sql
            except Exception as e:
                self.logger.error('SQL构造失败!!! %s'%str(e))

        def make_update_sql(index,key,tables_info):
            #构造update语句
            def if_int():
            #判断主键是不是int类型
                for i in tables_info:
                    if key == i[0] and 'int' in i[1]:
                        return True
                return False
            try:
                data_sql = ''
                data_sql1 = ''
                tables_info = set(tables_info)
                if if_int():
                    #主键是int类型
                    #判断主键是否存在此值,存在则构造更新sql，不存在不构造
                    if_sql = "SELECT COUNT({})  FROM `{}` WHERE {}='{}'".format(key,self.table_name,key,index)
                    cursor.execute(if_sql)
                    out_if = cursor.fetchall()[0][0]
                    if str(out_if) == '1':
                        for i in tables_info:
                            if 'int' in i[1]:
                                if int(self.update_int_data) != 0:
                                    data_sql = data_sql + i[0] + "='" + str(int(self.update_int_data) + index) + "'" + ','
                                    data_sql1 = data_sql1 + i[0] + "='" + str(int(self.update_int_data) + index) + "'" + ','
                            elif 'char' in i[1]:
                                if self.update_varchar_data == 'radom_uuid':
                                    data_sql = data_sql + i[0] + "='" + str(uuid.uuid1()) + str(uuid.uuid1()) + "'" + ','
                                    data_sql1 = data_sql1 + i[0] + "='" + str(uuid.uuid1()) + str(uuid.uuid1()) + "'" + ','
                                elif self.update_varchar_data != '0':
                                    data_sql = data_sql + i[0] + "='" + self.update_varchar_data + "'" + ','
                                    data_sql1 = data_sql1 + i[0] + "='" + self.update_varchar_data + "'" + ','
                                else:pass
                            elif 'float' in i[1]:
                                if self.update_float_data == '0':
                                    pass
                                else:
                                    data_sql = data_sql + i[0] + "='" + self.update_float_data + "'" + ','
                                    data_sql1 = data_sql1 + i[0] + "='" + self.update_float_data + "'" + ','
                            elif 'date' in i[1]:
                                if self.update_time_data == 'now':
                                    data_sql = data_sql + i[0] + "='" + time.strftime("%Y-%m-%d %X") + "'" + ','
                                    data_sql1 = data_sql1 + i[0] + "='" + time.strftime("%Y-%m-%d %X") + "'" + ','
                                elif self.update_time_data == '0':
                                    pass
                                else:
                                    data_sql = data_sql + "'" + self.insert_time_data + "'" + ','
                                    data_sql1 = data_sql1 + "'" + self.insert_time_data + "'" + ','

                            elif 'blob' in i[1]:
                                if self.update_blob_data == '0':
                                    pass
                                elif self.update_blob_data == 'default':
                                    data_sql = data_sql + i[0] + "=" + random.choice(self.payload_list) + ','
                                    data_sql1 = data_sql1 + i[0] + "='" + '数据过长不显示' + "'" + ','
                                else:
                                    data_sql = data_sql + i[0] + "=" + return_payload(self.update_blob_data) + ','
                                    data_sql1 = data_sql1 + i[0] + "='" + '数据过长不显示' + "'" + ','
                        update_sql = "UPDATE `%s` set "%self.table_name + data_sql[:-1] + "WHERE %s=%d"%(key,index)
                        update_sql1 = "UPDATE `%s` set "%self.table_name + data_sql1[:-1] + "WHERE %s=%d"%(key,index)
                        if self.sql_log == '1':
                            self.logger.info('SQL:%s' % update_sql1)
                        return (update_sql,True)
                    else:
                        self.logger.info('主键:%s  主键值:%d不存在，不构造更新语句!!!' % (key,index))
                        return (None,False)
            except Exception as e:
                self.logger.error('SQL构造失败!!! %s'%str(e))

        def mysql_insert(thread_number):
            # 连接mysql数据库
            try:
                db = pymysql.connect(host=self.ip, user=self.username, passwd=self.password, db=self.db_name,
                                     port=int(self.port))
                cursor = db.cursor()
            except Exception as e:
                self.logger.error('连接失败!!!' + str(e))
            if int(self.data_number) == 0:
                self.data_number = -1
            #获取字段类型
            key = get_tables_key()
            tables_info = get_data_type()
            if self.insert_for == '0':
                self.insert_for= 99999999
            index_big = 1
            index = int(self.insert_int_start) + int(thread_number - 1) * int(self.data_number)
            while index_big != int(self.insert_for)+1:
                try:
                    while index != int(thread_number)*int(self.data_number) + (index_big-1)*int(self.data_number) + int(self.insert_int_start):
                        try:
                            sql = make_insert_sql(index,tables_info)
                            cursor.execute(sql)
                            #self.logger.info('成功插入一条数据，主键为:{} 主键值:{}'.format(key,index))
                            if self.time_sleep != '0':
                                time.sleep(float(self.time_sleep))
                        except Exception as e:
                            self.logger.error('INSERT出错!!! 等待超时时间%d秒...  %s'%(int(self.error_sleep),str(e)))
                            time.sleep(float(self.error_sleep))
                            for i in range(5):
                                try:
                                    db = pymysql.connect(host=self.ip, user=self.username, passwd=self.password, db=self.db_name,port=int(self.port))
                                    cursor = db.cursor()
                                    cursor.execute(sql)
                                    cursor.execute('select version()')
                                    outinfo = cursor.fetchall()[0][0]
                                    self.logger.info('重试成功!!! 数据库版本:' + outinfo)
                                    break
                                except Exception as e:
                                    self.logger.error('尝试第(%d)次重试失败!!! 等待重试... 等待超时时间%d秒...  %s'%(i+1,int(self.error_sleep),str(e)))
                                    time.sleep(float(self.error_sleep))
                        finally:
                            db.commit()
                            index += 1
                except:pass
                finally:
                    self.logger.info('(%d).Commit !!! 提交%d条数据'%(index_big,int(self.data_number)))
                    index = (index_big)*int(self.data_number)+int(self.insert_int_start)
                    index_big += 1
                    if self.insert_for_time != '0':
                        time.sleep(float(self.insert_for_time))

        def mysql_update():
            # 连接mysql数据库
            try:
                db = pymysql.connect(host=self.ip, user=self.username, passwd=self.password, db=self.db_name,
                                     port=int(self.port))
                cursor = db.cursor()
            except Exception as e:
                self.logger.error('连接失败!!!' + str(e))
            if int(self.data_number) == 0:
                self.data_number = -1
            #获取字段类型
            tables_info = get_data_type()
            key = get_tables_key()
            index = int(self.update_int_start)
            while index != int(self.data_number) + int(self.update_int_start):
                try:
                    sql= make_update_sql(index,key,tables_info)
                    if sql[1] == True:
                        cursor.execute(sql[0])
                        db.commit()
                        #self.logger.info('成功更新一条数据，主键为:%s 主键值:%d'%(key,index))
                        if self.time_sleep != '0':
                            time.sleep(float(self.time_sleep))
                except Exception as e:
                    self.logger.error('UPDATE出错!!! 等待超时时间%d秒... \n%s'%(int(self.error_sleep),str(e)))
                    time.sleep(float(self.error_sleep))
                    for i in range(5):
                        try:
                            db = pymysql.connect(host=self.ip, user=self.username, passwd=self.password, db=self.db_name,port=int(self.port))
                            cursor = db.cursor()
                            cursor.execute(sql)
                            cursor.execute('select version()')
                            outinfo = cursor.fetchall()[0][0]
                            self.logger.info('重试成功!!! 数据库版本:' + outinfo)
                            break
                        except Exception as e:
                            self.logger.error('尝试第(%d)次重试失败!!! 等待重试... 等待超时时间%d秒...%s'%(i+1,int(self.error_sleep),str(e)))
                            time.sleep(float(self.error_sleep))
                finally:
                    index += 1

        def mysql_delete():
            # 连接mysql数据库
            try:
                db = pymysql.connect(host=self.ip, user=self.username, passwd=self.password, db=self.db_name,
                                     port=int(self.port))
                cursor = db.cursor()
            except Exception as e:
                self.logger.error('连接失败!!!' + str(e))
            key = get_tables_key()
            if int(self.data_number) == 0:
                self.data_number = -1
            if 'pt' in self.test_mode:
                index = 1
                delete_sql = """DELETE FROM `%s`.`%s` LIMIT 2000""" % (self.db_name,self.table_name)
                self.data_number = int(self.data_number)/2000
                while index != int(self.data_number) + 1:
                    try:
                        cursor.execute(delete_sql)
                        db.commit()
                        self.logger.info('成功删除两千条数据')
                        index += 1
                        if self.time_sleep != '0':
                            time.sleep(float(self.time_sleep))
                    except Exception as e:
                        if 'out of range' in str(e):
                            self.logger.info('所有数据已删除!!!')
                            break
                        else:
                            self.logger.error('删除失败!!! %s' % e)
                            time.sleep(float(self.error_sleep))
            else:
                index = 1
                select_sql = 'select %s from `%s` LIMIT 1' % (key, self.table_name)
                delete_sql = 'DELETE FROM `%s` LIMIT 1' % self.table_name
                if self.sql_log == '1':
                    self.logger.info('SQL:%s'%delete_sql)
                while index != int(self.data_number) + 1:
                    try:
                        cursor.execute(select_sql)
                        delete_info = cursor.fetchall()[0][0]
                        cursor.execute(delete_sql)
                        db.commit()
                        #self.logger.info('成功删除一条数据，主键为:{} 主键值为:{}'.format(key, delete_info))
                        index += 1
                        if self.time_sleep != '0':
                            time.sleep(float(self.time_sleep))
                    except Exception as e:
                        if 'out of range' in str(e):
                            self.logger.info('所有数据已删除!!!')
                            break
                        else:
                            self.logger.error('删除失败!!! %s' % e)
                            time.sleep(float(self.error_sleep))

        def mode_iud():
            # 连接mysql数据库
            try:
                db = pymysql.connect(host=self.ip, user=self.username, passwd=self.password, db=self.db_name,port=int(self.port))
                cursor = db.cursor()
            except Exception as e:
                self.logger.error('连接失败!!!' + str(e))
            if int(self.mode_iud_number) == 0:
                self.mode_iud_number = -1
                self.logger.info('循环次数:无限  每次数据量:%s' % (self.data_number))
            else:
                self.logger.info('循环次数:%s  每次数据量:%s' % (self.mode_iud_number, self.data_number))
            index = 1
            while index != int(self.mode_iud_number) + 1:
                try:
                    self.logger.info('第(%d)次增删改循环' % index)
                    mysql_insert(1)
                    time.sleep(int(self.mode_iud_sleep_time))
                    mysql_update()
                    time.sleep(int(self.mode_iud_sleep_time))
                    mysql_delete()
                    time.sleep(int(self.mode_iud_sleep_time))
                    index += 1
                except Exception as e:
                    self.logger.error('循环增删改失败!!! %s' % e)
                    time.sleep(float(self.error_sleep))
                    index += 1

        def mysql_custom():
            # 连接mysql数据库
            try:
                db = pymysql.connect(host=self.ip, user=self.username, passwd=self.password, db=self.db_name,port=int(self.port))
                cursor = db.cursor()
            except Exception as e:
                self.logger.error('连接失败!!!' + str(e))
            if int(self.data_number) == 0:
                self.data_number = -1
            index = 1
            while index != int(self.data_number) + 1:
                try:
                    cursor.connection.autocommit(True)
                    cursor.execute(self.custom_sql)
                    info = cursor.fetchall()
                    if self.sql_log == '1':
                        self.logger.info('(%d).结果:成功 返回值:%s 影响行:%s   SQL:%s' % (index, str(info), cursor.rowcount,self.custom_sql))
                    else:
                        self.logger.info('(%d).结果:成功 返回值:%s 影响行:%s'%(index,str(info),cursor.rowcount))
                    time.sleep(float(self.custom_sleep))
                except Exception as e:
                    self.logger.error('(%d).失败!!!%s SQL:%s'%(index,e,self.custom_sql))
                    time.sleep(float(self.error_sleep))
                    for i in range(5):
                        try:
                            db = pymysql.connect(host=self.ip, user=self.username, passwd=self.password,db=self.db_name, port=int(self.port))
                            cursor = db.cursor()
                            cursor.execute('select version()')
                            outinfo = cursor.fetchall()[0][0]
                            self.logger.info('重试成功!!! 数据库版本:' + outinfo)
                            break
                        except Exception as e:
                            self.logger.error(
                                '尝试第(%d)次重试失败!!! 等待重试... 等待超时时间%d秒...  %s' % (i + 1, int(self.error_sleep), str(e)))
                            time.sleep(float(self.error_sleep))
                finally:
                    index += 1

        def select_ds_table():
            # 连接mysql数据库
            try:
                db = pymysql.connect(host=self.ip, user=self.username, passwd=self.password, db=self.db_name,
                                     port=int(self.port))
                cursor = db.cursor()
            except Exception as e:
                self.logger.error('连接失败!!!' + str(e))
            select_sql = """select count(*) from %s.ds_%s"""%(self.db_name,self.table_name)
            while 1:
                cursor.execute(select_sql)
                outinfo1 = cursor.fetchall()[0][0]
                if int(outinfo1) == 0:
                    break
                time.sleep(1)
                cursor.execute(select_sql)
                outinfo2 = cursor.fetchall()[0][0]
                self.logger.info('临时表每秒增量:%d 总数:%d'%((int(outinfo2)-int(outinfo1)),int(outinfo2)))



        def mysql_performance():
            S_time = time.time()
            if self.test_mode == 'pt_insert':
                T1 = Thread(target=mysql_insert(1))
                T1.start()
                T1.join()
            elif self.test_mode == 'pt_update':
                T1 = Thread(target=mysql_update())
                T1.start()
                T1.join()
            elif self.test_mode == 'pt_delete':
                T1 = Thread(target=mysql_delete())
                T1.start()
                T1.join()
            else:pass

            T2 = Thread(target=select_ds_table)
            T2.start()
            T2.join()
            if 'delete' in self.test_mode:
                self.logger.info('性能测试_总数据量：%d 总时长：%d 速度为：%d条/秒'%(int(self.data_number)*2000,(time.time()-S_time),int(self.data_number)*2000/int((time.time()-S_time))))
            else:
                self.logger.info('性能测试_总数据量：%d 总时长：%d 速度为：%d条/秒'%(int(self.data_number),(time.time()-S_time),int(self.data_number)/int((time.time()-S_time))))



        try:
            T_list = []
            if self.test_mode == 'insert':
                for i in range(1,int(self.insert_thread)+1):
                    T = Thread(target=mysql_insert,args=(i,))
                    T.start()
                    time.sleep(0.1)
                    T_list.append(T)
                for t in T_list:
                    t.join()

            elif self.test_mode == 'update':
                mysql_update()

            elif self.test_mode == 'delete':
                mysql_delete()

            elif self.test_mode == 'mode_iud':
                mode_iud()

            elif self.test_mode == 'custom':
                mysql_custom()

            elif 'pt' in self.test_mode:
                mysql_performance()

            else:pass
        except Exception as e:
            self.logger.error('连接失败!!!%s'%e)
            time.sleep(float(self.error_sleep))

    def sqlserver(self):
        # 连接sqlserver数据库，显示版本
        try:
            db = pymssql.connect(self.ip, self.username, self.password, port=self.port, database=self.db_name)
            cursor = db.cursor()
            cursor.execute('select @@version')
            out_info = cursor.fetchall()[0][0]
            self.logger.info('数据库版本:' + str(out_info))
            self.logger.info('测试模式:%s' % self.test_mode)
        except Exception as e:
            self.logger.error('连接失败!!!' + str(e))

        def return_payload(path):
            with open(path, 'rb') as f:
                return'0x' + str(binascii.b2a_hex(f.read()))[2:-1]

        def get_data_type():
            # 获取表字段和数据类型来构造sql语句
            try:

                cursor.execute("""select COLUMN_NAME,DATA_TYPE from information_schema.COLUMNS where table_name='%s' and TABLE_CATALOG='%s' and TABLE_SCHEMA='dbo'""" % (self.table_name,self.db_name))
                tables_info = cursor.fetchall()
                tables_out_info = str(tables_info)
                self.logger.info('表字段和类型：%s ' % tables_out_info)
                return tables_info
            except Exception as e:
                self.logger.error('获取表名和字段失败!!! %s' % str(e))

        def get_tables_key():

            try:
                cursor.execute("""SELECT TABLE_NAME,COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE TABLE_name='%s'""" % (self.table_name))
                tables_key_info = cursor.fetchall()[0][1]
                self.logger.info('%s数据表 KEY为：%s ' % (self.table_name,str(tables_key_info)))
                return tables_key_info
            except Exception as e:
                self.logger.error('获取%s数据表KEY失败!!! %s' % (self.table_name,str(e)))

        def make_insert_sql(index,tables_info):
            #构造insert语句
            try:
                filed_sql = ''
                data_sql = ''
                filed_sql1 = ''
                data_sql1 = ''
                tables_info = set(tables_info)
                for i in tables_info:
                    i[1].encode('gbk')
                    if 'numer' in i[1] or 'int' in i[1]:
                        filed_sql = filed_sql  + i[0]  + ','
                        data_sql = data_sql + '%d' % index + ','
                        filed_sql1 = filed_sql1  + i[0]  + ','
                        data_sql1 = data_sql1 + '%d' % index + ','

                    elif 'char' in i[1]:
                        filed_sql = filed_sql +  i[0]  + ','
                        filed_sql1 = filed_sql1 + i[0] + ','
                        if self.insert_varchar_data == 'random_uuid':
                            data_sql = data_sql + "'" + str(uuid.uuid1()) + '-' + str(uuid.uuid1()) + "'" + ','
                            data_sql1 = data_sql1 + "'" + str(uuid.uuid1()) + '-' + str(uuid.uuid1()) + "'" + ','
                        else:
                            data_sql = data_sql + "'" + self.insert_varchar_data + "'" + ','
                            data_sql1 = data_sql1 + "'" + self.insert_varchar_data + "'" + ','

                    elif 'real' in i[1] or 'float' in i[1]:
                        filed_sql = filed_sql +  i[0] +  ','
                        data_sql = data_sql + str(self.insert_float_data)  + ','
                        filed_sql1 = filed_sql1 +  i[0] +  ','
                        data_sql1 = data_sql1  + str(self.insert_float_data) + ','

                    elif 'date' in i[1]:
                        filed_sql = filed_sql +  i[0] + ','
                        filed_sql1 = filed_sql1 +  i[0] + ','
                        if self.insert_time_data == 'now':
                            data_sql = data_sql + "'" + time.strftime("%Y-%m-%d %X") + "'" + ','
                            data_sql1 = data_sql1 + "'" + time.strftime("%Y-%m-%d %X") + "'" + ','
                        else:
                            data_sql = data_sql + "'" + self.insert_time_data + "'" + ','
                            data_sql1 = data_sql1 + "'" + self.insert_time_data + "'" + ','

                    elif 'image' in i[1] or 'bin' in i[1]:
                        filed_sql = filed_sql +  i[0] +  ','
                        filed_sql1 = filed_sql1 +  i[0]  + ','
                        if self.insert_blob_data == 'default':
                            data_sql = data_sql + random.choice(self.payload_list) + ','
                            data_sql1 = data_sql1 + '数据过长不显示' + ','
                        else:
                            data_sql = data_sql + return_payload(self.insert_blob_data) + ','
                            data_sql1 = data_sql1 + '数据过长不显示' + ','

                    else:
                        filed_sql = filed_sql  + i[0] +  ','
                        data_sql = data_sql + 'null' + ','
                sql = 'INSERT INTO %s ' % self.table_name + '(' + filed_sql[:-1] + ')' + ' VALUES ' + '(' + data_sql[:-1] + ")"
                out_sql = 'INSERT INTO %s ' % self.table_name + '(' + filed_sql1[:-1] + ')' + ' VALUES ' + '(' + data_sql1[:-1] + ")"
                if self.sql_log == '1':
                    self.logger.info('SQL:%s'%str(out_sql))
                return sql
            except Exception as e:
                self.logger.error('SQL构造失败!!! %s'%str(e))

        def make_update_sql(index,key,tables_info):
            #构造update语句
            def if_int():
            #判断主键是不是int类型
                for i in tables_info:
                    if key == i[0] and 'numer' in i[1] or key == i[0] and 'int' in i[1]:
                        return True
                return False

            try:
                data_sql = ''
                data_sql1 = ''
                tables_info = set(tables_info)
                if if_int():
                    #主键是int类型
                    #判断主键是否存在此值,存在则构造更新sql，不存在不构造
                    if_sql = "SELECT COUNT({})  FROM {} WHERE {}='{}'".format(key,self.table_name,key,index)
                    cursor.execute(if_sql)
                    out_if = cursor.fetchall()[0][0]

                    if str(out_if) == '1':
                        for i in tables_info:
                            if 'numer' in i[1] or 'int' in i[1]:
                                if int(self.update_int_data) != 0:
                                    data_sql = data_sql + i[0] + "='" + str(int(self.update_int_data) + index) + "'" + ','
                                    data_sql1 = data_sql1 + i[0] + "='" + str(int(self.update_int_data) + index) + "'" + ','
                            elif 'char' in i[1]:
                                if self.update_varchar_data == 'radom_uuid':
                                    data_sql = data_sql + i[0] + "='" + str(uuid.uuid1()) + str(uuid.uuid1()) + "'" + ','
                                    data_sql1 = data_sql1 + i[0] + "='" + str(uuid.uuid1()) + str(uuid.uuid1()) + "'" + ','
                                elif self.update_varchar_data != '0':
                                    data_sql = data_sql + i[0] + "='" + self.update_varchar_data + "'" + ','
                                    data_sql1 = data_sql1 + i[0] + "='" + self.update_varchar_data + "'" + ','
                                else:pass
                            elif 'real' in i[1] or 'float' in i[1]:
                                if self.update_float_data == '0':
                                    pass
                                else:
                                    data_sql = data_sql + i[0] + "='" + self.update_float_data + "'" + ','
                                    data_sql1 = data_sql1 + i[0] + "='" + self.update_float_data + "'" + ','
                            elif 'date' in i[1]:
                                if self.update_time_data == 'now':
                                    data_sql = data_sql + i[0] + "='" + time.strftime("%Y-%m-%d %X") + "'" + ','
                                    data_sql1 = data_sql1 + i[0] + "='" + time.strftime("%Y-%m-%d %X") + "'" + ','
                                elif self.update_time_data == '0':
                                    pass
                                else:
                                    data_sql = data_sql + "'" + self.insert_time_data + "'" + ','
                                    data_sql1 = data_sql1 + "'" + self.insert_time_data + "'" + ','

                            elif 'image' in i[1] or 'bin' in i[1]:
                                if self.update_blob_data == '0':
                                    pass
                                elif self.update_blob_data == 'default':
                                    data_sql = data_sql + i[0] + "='" + random.choice(self.payload_list) + "'" + ','
                                    data_sql1 = data_sql1 + i[0] + "='" + '数据过长不显示' + "'" + ','
                                else:
                                    data_sql = data_sql + i[0] + "='" + return_payload(self.update_blob_data) + "'" + ','
                                    data_sql1 = data_sql1 + i[0] + "='" + '数据过长不显示' + "'" + ','
                        update_sql = "UPDATE %s set "%self.table_name + data_sql[:-1] + "WHERE %s=%d"%(key,index)
                        update_sql1 = "UPDATE %s set "%self.table_name + data_sql1[:-1] + "WHERE %s=%d"%(key,index)
                        if self.sql_log == '1':
                            self.logger.info('SQL:%s' % update_sql1)
                        return (update_sql,True)
                    else:
                        self.logger.info('主键:%s  主键值:%d不存在，不构造更新语句!!!' % (key,index))
                        return (None,False)
            except Exception as e:
                self.logger.error('SQL构造失败!!! %s'%str(e))

        def sqlserver_insert():
            # 连接sqlserver数据库，显示版本
            try:
                db = pymssql.connect(self.ip, self.username, self.password, port=self.port, database=self.db_name)
                cursor = db.cursor()
            except Exception as e:
                self.logger.error('连接失败!!!' + str(e))

            if int(self.data_number) == 0:
                self.data_number = -1
            # 获取字段类型
            tables_info = get_data_type()
            key = get_tables_key()
            if self.insert_for == '0':
                self.insert_for = 99999999
            index_big = 1
            index = int(self.insert_int_start)
            while index_big != int(self.insert_for) + 1:
                try:
                    while index != int(self.data_number) + (index_big-1)*int(self.data_number) + int(self.insert_int_start):
                        try:
                            sql = make_insert_sql(index,tables_info)
                            cursor.execute(sql)
                            #self.logger.info('成功插入一条数据，主键为:%s 主键值:%d' % (str(key), index))
                            if self.time_sleep != '0':
                                time.sleep(float(self.time_sleep))

                        except Exception as e:
                            self.logger.error('INSERT出错!!! 超时时间%d秒... %s' % (int(self.error_sleep), str(e)))
                            time.sleep(float(self.error_sleep))
                            for i in range(5):
                                try:
                                    db = pymssql.connect(self.ip, self.username, self.password, port=self.port,database=self.db_name)
                                    cursor = db.cursor()
                                    cursor.execute(sql)
                                    cursor.execute('select @@version')
                                    outinfo = cursor.fetchall()[0][0]
                                    self.logger.info('重试成功!!! 数据库版本:' + outinfo)
                                    break
                                except Exception as e:
                                    self.logger.error('尝试第(%d)次重试失败!!! 等待重试... 等待超时时间%d秒...%s' % (i + 1, int(self.error_sleep), str(e)))
                                    time.sleep(float(self.error_sleep))
                        finally:
                            db.commit()
                            index += 1
                except:pass
                finally:
                    self.logger.info('(%d).Commit !!! 提交%d条数据'%(index_big,int(self.data_number)))
                    index = (index_big)*int(self.data_number)+int(self.insert_int_start)
                    index_big += 1
                    if self.insert_for_time != '0':
                        time.sleep(float(self.insert_for_time))

        def sqlserver_update():
            # 连接sqlserver数据库
            try:
                db = pymssql.connect(self.ip, self.username, self.password, port=self.port, database=self.db_name)
                cursor = db.cursor()
            except Exception as e:
                self.logger.error('连接失败!!!' + str(e))
            if int(self.data_number) == 0:
                self.data_number = -1
            # 获取字段类型
            tables_info = get_data_type()
            key = get_tables_key()
            index = int(self.update_int_start)
            while index != int(self.data_number) + int(self.update_int_start):
                try:
                    sql = make_update_sql(index, key, tables_info)
                    if sql[1] == True:
                        cursor.execute(sql[0])
                        db.commit()
                        self.logger.info('成功更新一条数据，主键为:%s 主键值:%d' % (key, index))
                        time.sleep(float(self.time_sleep))
                except Exception as e:
                    self.logger.error('UPDATE出错!!! 等待超时时间%d秒... \n%s' % (int(self.error_sleep), str(e)))
                    time.sleep(float(self.error_sleep))
                    for i in range(5):
                        try:
                            db = pymysql.connect(host=self.ip, user=self.username, passwd=self.password,db=self.db_name, port=int(self.port))
                            cursor = db.cursor()
                            cursor.execute(sql)
                            cursor.execute('select version()')
                            outinfo = cursor.fetchall()[0][0]
                            self.logger.info('重试成功!!! 数据库版本:' + outinfo)
                            break
                        except Exception as e:
                            self.logger.error(
                                '尝试第(%d)次重试失败!!! 等待重试... 等待超时时间%d秒...%s' % (i + 1, int(self.error_sleep), str(e)))
                            time.sleep(float(self.error_sleep))
                finally:
                    index += 1

        def sqlserver_delete():
            # 连接sqlserver数据库
            try:
                db = pymssql.connect(self.ip, self.username, self.password, port=self.port, database=self.db_name)
                cursor = db.cursor()
            except Exception as e:
                self.logger.error('连接失败!!!' + str(e))
            key = get_tables_key()
            if int(self.data_number) == 0:
                self.data_number = -1
            index = 1
            select_sql = 'SELECT TOP 1 %s FROM %s' % (key, self.table_name)
            delete_sql = 'DELETE TOP(1) FROM %s' % self.table_name
            if self.sql_log == '1':
                self.logger.info('SQL:%s' % delete_sql)
            while index != int(self.data_number) + 1:
                try:
                    cursor.execute(select_sql)
                    delete_info = cursor.fetchall()[0][0]
                    cursor.execute(delete_sql)
                    db.commit()
                    self.logger.info('成功删除一条数据，主键为:{} 主键值为:{}'.format(key, delete_info))
                    index += 1
                    time.sleep(float(self.time_sleep))
                except Exception as e:
                    if 'out of range' in str(e):
                        self.logger.info('所有数据已删除!!!')
                        break
                    else:
                        self.logger.error('删除失败!!! %s' % e)
                        time.sleep(float(self.error_sleep))

        def sqlserver_iud():
            # 连接sqlserver数据库
            try:
                db = pymssql.connect(self.ip, self.username, self.password, port=self.port, database=self.db_name)
                cursor = db.cursor()
            except Exception as e:
                self.logger.error('连接失败!!!' + str(e))
            if int(self.mode_iud_number) == 0:
                self.mode_iud_number = -1
                self.logger.info('循环次数:无限  每次数据量:%s' % (self.data_number))
            else:
                self.logger.info('循环次数:%s  每次数据量:%s' % (self.mode_iud_number, self.data_number))
            index = 1
            while index != int(self.mode_iud_number) + 1:
                try:
                    self.logger.info('第(%d)次增删改循环' % index)
                    sqlserver_insert()
                    time.sleep(int(self.mode_iud_sleep_time))
                    sqlserver_update()
                    time.sleep(int(self.mode_iud_sleep_time))
                    sqlserver_delete()
                    time.sleep(int(self.mode_iud_sleep_time))
                    index += 1
                except Exception as e:
                    self.logger.error('循环增删改失败!!! %s' % e)
                    time.sleep(float(self.error_sleep))
                    index += 1

        def sqlserver_custom():
            # 连接sqlserver数据库
            try:
                db = pymssql.connect(self.ip, self.username, self.password, port=self.port, database=self.db_name)
                cursor = db.cursor()
            except Exception as e:
                self.logger.error('连接失败!!!' + str(e))

            if int(self.data_number) == 0:
                self.data_number = -1
            index = 1
            while index != int(self.data_number) + 1:
                try:
                    cursor.connection.autocommit(True)
                    cursor.execute(self.custom_sql)
                    if 'update' in self.custom_sql or 'UPDATE' in self.custom_sql or 'delete' in self.custom_sql or 'delete' in self.custom_sql:
                        info = 'SQL无返回值'
                    else:
                        info = cursor.fetchall()
                    if self.sql_log == '1':
                        self.logger.info('(%d).结果:成功 返回值:%s 影响行:%s   SQL:%s' % (index, str(info), cursor.rowcount,self.custom_sql))
                    else:
                        self.logger.info('(%d).结果:成功 返回值:%s 影响行:%s'%(index,str(info),cursor.rowcount))
                    time.sleep(float(self.custom_sleep))
                except Exception as e:
                    self.logger.error('(%d).失败!!!%s SQL:%s'%(index,e,self.custom_sql))
                    time.sleep(float(self.error_sleep))
                    for i in range(5):
                        try:
                            db = pymssql.connect(self.ip, self.username, self.password, port=self.port,database=self.db_name)
                            cursor = db.cursor()
                            cursor.execute(self.custom_sql)
                            cursor.execute('select @@version')
                            outinfo = cursor.fetchall()[0][0]
                            self.logger.info('重试成功!!! 数据库版本:' + outinfo)
                            break
                        except Exception as e:
                            self.logger.error(
                                '尝试第(%d)次重试失败!!! 等待重试... 等待超时时间%d秒...  %s' % (i + 1, int(self.error_sleep), str(e)))
                            time.sleep(float(self.error_sleep))
                finally:
                    index += 1

        try:
            if self.test_mode == 'insert':
                sqlserver_insert()

            elif self.test_mode == 'update':
                sqlserver_update()

            elif self.test_mode == 'delete':
                sqlserver_delete()

            elif self.test_mode == 'mode_iud':
                sqlserver_iud()

            elif self.test_mode == 'custom':
                sqlserver_custom()

            else:pass
        except Exception as e:
            self.logger.error('连接失败!!!%s'%e)
            time.sleep(float(self.error_sleep))

    def oracle(self):
        # 连接oracler数据库，显示版本
        try:
            db = pyoracle.connect(self.username, self.password, self.ip + ':' + self.port + '/' + self.db_name)
            cursor = db.cursor()
            sql = '''select * from v$version'''  # sql语句
            cursor.execute(sql)
            row = cursor.fetchall()[0][0]
            self.logger.info('数据库版本:' + str(row))
            self.logger.info('测试模式:%s' % self.test_mode)
        except Exception as e:
            self.logger.error('连接失败!!!' + str(e))

        def return_payload(path):
            with open(path, 'rb') as f:
                return '0x' + str(binascii.b2a_hex(f.read()))[2:-1]

        def get_data_type():
            # 获取表字段和数据类型来构造sql语句
            try:
                cursor.execute("""select COLUMN_NAME,DATA_TYPE from user_tab_cols where table_name='%s'""" % self.table_name)
                tables_info = cursor.fetchall()
                tables_out_info = str(tables_info)
                if tables_info == []:
                    self.logger.error('获取表名和字段失败!!!  1.使用最高权限用户登录 2.创建表时使用大写来创建(小写创建虽然显示为大写实际获取不到)')
                else:
                    self.logger.info('表字段和类型：%s ' % tables_out_info)
                return tables_info
            except Exception as e:
                self.logger.error('获取表名和字段失败!!! %s' % str(e))

        def get_tables_key():

            try:
                sql = """select
                 col.column_name
                from
                 user_constraints con,user_cons_columns col
                where
                 con.constraint_name=col.constraint_name and con.constraint_type='P'
                 and col.table_name='%s'"""%self.table_name
                cursor.execute(sql)
                tables_key_info = cursor.fetchall()[0][0]
                self.logger.info('%s数据表 KEY为：%s ' % (self.table_name,str(tables_key_info)))
                return tables_key_info
            except Exception as e:
                self.logger.error('获取%s数据表KEY失败!!! %s' % (self.table_name,str(e)))

        def make_insert_sql(index,tables_info):
            #构造insert语句
            try:
                filed_sql = ''
                data_sql = ''
                filed_sql1 = ''
                data_sql1 = ''
                tables_info = set(tables_info)
                for i in tables_info:
                    i[1].encode('gbk')
                    if 'NUMBER' in i[1] or 'INT' in i[1]:
                        filed_sql = filed_sql  + i[0]  + ','
                        data_sql = data_sql + '%d' % index + ','
                        filed_sql1 = filed_sql1  + i[0]  + ','
                        data_sql1 = data_sql1 + '%d' % index + ','

                    elif 'CHAR' in i[1]:
                        filed_sql = filed_sql +  i[0]  + ','
                        filed_sql1 = filed_sql1 + i[0] + ','
                        if self.insert_varchar_data == 'random_uuid':
                            data_sql = data_sql + "'" + str(uuid.uuid1()) + '-' + str(uuid.uuid1()) + "'" + ','
                            data_sql1 = data_sql1 + "'" + str(uuid.uuid1()) + '-' + str(uuid.uuid1()) + "'" + ','
                        else:
                            data_sql = data_sql + "'" + self.insert_varchar_data + "'" + ','
                            data_sql1 = data_sql1 + "'" + self.insert_varchar_data + "'" + ','

                    elif 'BINARY' in i[1] or 'FLOAT' in i[1]:
                        filed_sql = filed_sql +  i[0] +  ','
                        data_sql = data_sql + str(self.insert_float_data)  + ','
                        filed_sql1 = filed_sql1 +  i[0] +  ','
                        data_sql1 = data_sql1  + str(self.insert_float_data) + ','

                    elif 'DATE' in i[1] or 'TIME' in i[1]:
                        filed_sql = filed_sql +  i[0] + ','
                        filed_sql1 = filed_sql1 +  i[0] + ','
                        if self.insert_time_data == 'now':
                            data_sql = data_sql  +  "to_date('%s','YYYY-MM-DD HH24:MI:SS')"%time.strftime("%Y-%m-%d %X") + ','
                            data_sql1 = data_sql1 + "to_date('%s','YYYY-MM-DD HH24:MI:SS')"%time.strftime("%Y-%m-%d %X") + "'" + ','
                        else:
                            data_sql = data_sql + "'" + self.insert_time_data + "'" + ','
                            data_sql1 = data_sql1 + "'" + self.insert_time_data + "'" + ','

                    elif 'LOB' in i[1] or 'RAW' in i[1]:
                        filed_sql = filed_sql +  i[0] +  ','
                        filed_sql1 = filed_sql1 +  i[0]  + ','
                        if self.insert_blob_data == 'default':
                            data_sql = data_sql + "HEXTORAW('%s')"%(random.choice(self.oracle_payloads_list)) + ','
                            data_sql1 = data_sql1 + '数据过长不显示' + ','
                        else:
                            data_sql = data_sql + "HEXTORAW('%s')"%(return_payload(self.insert_blob_data)[2:]) + ','
                            data_sql1 = data_sql1 + '数据过长不显示' + ','

                    else:
                        filed_sql = filed_sql  + i[0] +  ','
                        data_sql = data_sql + 'null' + ','
                sql = 'INSERT INTO %s ' % self.table_name + '(' + filed_sql[:-1] + ')' + ' VALUES ' + '(' + data_sql[:-1] + ")"
                out_sql = 'INSERT INTO %s ' % self.table_name + '(' + filed_sql1[:-1] + ')' + ' VALUES ' + '(' + data_sql1[:-1] + ")"
                if self.sql_log == '1':
                    self.logger.info('SQL:%s'%str(out_sql))
                return sql
            except Exception as e:
                self.logger.error('SQL构造失败!!! %s'%str(e))

        def make_update_sql(index,key,tables_info):
            # 构造update语句
            def if_int():
                # 判断主键是不是int类型
                for i in tables_info:
                    if key == i[0] and 'NUMBER' in i[1] or key == i[0] and 'INT' in i[1]:
                        return True
                return False

            try:
                data_sql = ''
                data_sql1 = ''
                tables_info = set(tables_info)
                if if_int():
                    # 主键是int类型
                    # 判断主键是否存在此值,存在则构造更新sql，不存在不构造
                    if_sql = "SELECT COUNT({})  FROM {} WHERE {}='{}'".format(key, self.table_name, key, index)
                    cursor.execute(if_sql)
                    out_if = cursor.fetchall()[0][0]

                    if str(out_if) == '1':
                        for i in tables_info:
                            if 'NUMBER' in i[1] or 'INT' in i[1]:
                                if int(self.update_int_data) != 0:
                                    data_sql = data_sql + i[0] + "='" + str(
                                        int(self.update_int_data) + index) + "'" + ','
                                    data_sql1 = data_sql1 + i[0] + "='" + str(
                                        int(self.update_int_data) + index) + "'" + ','
                            elif 'CHAR' in i[1]:
                                if self.update_varchar_data == 'radom_uuid':
                                    data_sql = data_sql + i[0] + "='" + str(uuid.uuid1()) + str(
                                        uuid.uuid1()) + "'" + ','
                                    data_sql1 = data_sql1 + i[0] + "='" + str(uuid.uuid1()) + str(
                                        uuid.uuid1()) + "'" + ','
                                elif self.update_varchar_data != '0':
                                    data_sql = data_sql + i[0] + "='" + self.update_varchar_data + "'" + ','
                                    data_sql1 = data_sql1 + i[0] + "='" + self.update_varchar_data + "'" + ','
                                else:
                                    pass
                            elif 'BINARY' in i[1] or 'FLOAT' in i[1]:
                                if self.update_float_data == '0':
                                    pass
                                else:
                                    data_sql = data_sql + i[0] + "='" + self.update_float_data + "'" + ','
                                    data_sql1 = data_sql1 + i[0] + "='" + self.update_float_data + "'" + ','
                            elif 'DATE' in i[1] or 'TIME' in i[1]:
                                if self.update_time_data == 'now':
                                    data_sql = data_sql + i[0] + "=" + "to_date('%s','YYYY-MM-DD HH24:MI:SS')"%time.strftime("%Y-%m-%d %X")  + ','
                                    data_sql1 = data_sql1 + i[0] + "=" + "to_date('%s','YYYY-MM-DD HH24:MI:SS')"%time.strftime("%Y-%m-%d %X")  + ','
                                elif self.update_time_data == '0':
                                    pass
                                else:
                                    data_sql = data_sql + "'" + self.insert_time_data + "'" + ','
                                    data_sql1 = data_sql1 + "'" + self.insert_time_data + "'" + ','
                            elif 'LOB' in i[1] or 'RAW' in i[1]:
                                if self.update_blob_data == '0':
                                    pass
                                elif self.update_blob_data == 'default':
                                    data_sql = data_sql + i[0] + "=" + "HEXTORAW('%s')"%(random.choice(self.oracle_payloads_list)) + ','
                                    data_sql1 = data_sql1 + i[0] + "=" + '数据过长不显示'  + ','
                                else:
                                    data_sql = data_sql + i[0] + "=" + "HEXTORAW('%s')"%(return_payload(self.insert_blob_data)[2:]) + ','
                                    data_sql1 = data_sql1 + i[0] + "=" + '数据过长不显示' + ','
                        update_sql = "UPDATE %s set " % self.table_name + data_sql[:-1] + " WHERE %s=%d" % (key, index)
                        update_sql1 = "UPDATE %s set " % self.table_name + data_sql1[:-1] + " WHERE %s=%d" % (key, index)
                        if self.sql_log == '1':
                            self.logger.info('SQL:%s' % update_sql1)
                        return (update_sql, True)
                    else:
                        self.logger.info('主键:%s  主键值:%d不存在，不构造更新语句!!!' % (key, index))
                        return (None, False)
            except Exception as e:
                self.logger.error('SQL构造失败!!! %s' % str(e))

        def oracle_insert():
            # 连接oracle数据库，显示版本
            try:
                db = pyoracle.connect(self.username, self.password,self.ip + ':' + self.port + '/' + self.db_name)
                cursor = db.cursor()
            except Exception as e:
                self.logger.error('连接失败!!!' + str(e))

            if int(self.data_number) == 0:
                self.data_number = -1
            # 获取字段类型
            tables_info = get_data_type()
            key = get_tables_key()
            index = int(self.insert_int_start)
            if self.insert_for == '0':
                self.insert_for = 99999999
            index_big = 1
            index = int(self.insert_int_start)
            while index_big != int(self.insert_for) + 1:
                try:
                    while index != int(self.data_number) + (index_big-1)*int(self.data_number) + int(self.insert_int_start):
                        try:
                            sql = make_insert_sql(index,tables_info)
                            cursor.execute(sql)
                            #self.logger.info('成功插入一条数据，主键为:%s 主键值:%d' % (str(key), index))
                            time.sleep(float(self.time_sleep))
                        except Exception as e:
                            self.logger.error('INSERT出错!!! 超时时间%d秒... %s' % (int(self.error_sleep), str(e)))
                            time.sleep(float(self.error_sleep))
                            for i in range(5):
                                try:
                                    db = pyoracle.connect(self.username, self.password,self.ip + ':' + self.port + '/' + self.db_name)
                                    cursor = db.cursor()
                                    cursor.execute(sql)
                                    cursor.execute('select * from v$version')
                                    outinfo = cursor.fetchall()[0][0]
                                    self.logger.info('重试成功!!! 数据库版本:' + outinfo)
                                    break
                                except Exception as e:
                                    self.logger.error('尝试第(%d)次重试失败!!! 等待重试... 等待超时时间%d秒...%s' % (i + 1, int(self.error_sleep), str(e)))
                                    time.sleep(float(self.error_sleep))
                        finally:
                            index += 1
                            db.commit()
                except:pass
                finally:
                    self.logger.info('(%d).Commit !!! 提交%d条数据'%(index_big,int(self.data_number)))
                    index = (index_big)*int(self.data_number)+int(self.insert_int_start)
                    index_big += 1
                    if self.insert_for_time != '0':
                        time.sleep(float(self.insert_for_time))

        def oracle_update():
            # 连接oracle数据库
            try:
                db = pyoracle.connect(self.username, self.password, self.ip + ':' + self.port + '/' + self.db_name)
                cursor = db.cursor()
            except Exception as e:
                self.logger.error('连接失败!!!' + str(e))
            if int(self.data_number) == 0:
                self.data_number = -1
            # 获取字段类型
            tables_info = get_data_type()
            key = get_tables_key()
            index = int(self.update_int_start)
            while index != int(self.data_number) + int(self.update_int_start):
                try:
                    sql = make_update_sql(index, key, tables_info)
                    if sql[1] == True:
                        cursor.execute(sql[0])
                        db.commit()
                        self.logger.info('成功更新一条数据，主键为:%s 主键值:%d' % (key, index))
                        time.sleep(float(self.time_sleep))
                except Exception as e:
                    self.logger.error('UPDATE出错!!! 等待超时时间%d秒... \n%s' % (int(self.error_sleep), str(e)))
                    time.sleep(float(self.error_sleep))
                    for i in range(5):
                        try:
                            db = pyoracle.connect(self.username, self.password,
                                                  self.ip + ':' + self.port + '/' + self.db_name)
                            cursor = db.cursor()
                            cursor.execute(sql)
                            cursor.execute('select version()')
                            outinfo = cursor.fetchall()[0][0]
                            self.logger.info('重试成功!!! 数据库版本:' + outinfo)
                            break
                        except Exception as e:
                            self.logger.error(
                                '尝试第(%d)次重试失败!!! 等待重试... 等待超时时间%d秒...%s' % (i + 1, int(self.error_sleep), str(e)))
                            time.sleep(float(self.error_sleep))
                finally:
                    index += 1

        def oracle_delete():
            # 连接oracle数据库
            try:
                db = pyoracle.connect(self.username, self.password, self.ip + ':' + self.port + '/' + self.db_name)
                cursor = db.cursor()
            except Exception as e:
                self.logger.error('连接失败!!!' + str(e))
            key = get_tables_key()
            if int(self.data_number) == 0:
                self.data_number = -1
            index = 1
            select_sql = """select %s from (select %s from %s order by %s) where rownum=1""" % (key,key, self.table_name,key)
            delete_sql = """DELETE FROM "%s" WHERE ROWNUM = 1""" % self.table_name
            if self.sql_log == '1':
                self.logger.info('SQL:%s' % delete_sql)
            while index != int(self.data_number) + 1:
                try:
                    cursor.execute(select_sql)
                    delete_info = cursor.fetchall()[0][0]
                    cursor.execute(delete_sql)
                    db.commit()
                    self.logger.info('成功删除一条数据，主键为:{} 主键值为:{}'.format(key, delete_info))
                    time.sleep(float(self.time_sleep))
                except Exception as e:
                    if 'out of range' in str(e):
                        self.logger.info('所有数据已删除!!!')
                        break
                    else:
                        self.logger.error('删除失败!!! %s' % e)
                        time.sleep(float(self.error_sleep))
                finally:index += 1

        def oracle_iud():
            # 连接sqlserver数据库
            try:
                db = pyoracle.connect(self.username, self.password, self.ip + ':' + self.port + '/' + self.db_name)
                cursor = db.cursor()
            except Exception as e:
                self.logger.error('连接失败!!!' + str(e))
            if int(self.mode_iud_number) == 0:
                self.mode_iud_number = -1
                self.logger.info('循环次数:无限  每次数据量:%s' % (self.data_number))
            else:
                self.logger.info('循环次数:%s  每次数据量:%s' % (self.mode_iud_number, self.data_number))
            index = 1
            while index != int(self.mode_iud_number) + 1:
                try:
                    self.logger.info('第(%d)次增删改循环' % index)
                    oracle_insert()
                    time.sleep(int(self.mode_iud_sleep_time))
                    oracle_update()
                    time.sleep(int(self.mode_iud_sleep_time))
                    oracle_delete()
                    time.sleep(int(self.mode_iud_sleep_time))
                    index += 1
                except Exception as e:
                    self.logger.error('循环增删改失败!!! %s' % e)
                    time.sleep(float(self.error_sleep))
                    index += 1

        def oracle_custom():
            # 连接oracle数据库
            try:
                db = pyoracle.connect(self.username, self.password, self.ip + ':' + self.port + '/' + self.db_name)
                cursor = db.cursor()
            except Exception as e:
                self.logger.error('连接失败!!!' + str(e))

            if int(self.data_number) == 0:
                self.data_number = -1
            index = 1
            while index != int(self.data_number) + 1:
                try:
                    cursor.execute(self.custom_sql)
                    db.commit()
                    if 'update' in self.custom_sql or 'UPDATE' in self.custom_sql or 'delete' in self.custom_sql or 'delete' in self.custom_sql:
                        info = 'SQL无返回值'
                    else:
                        info = cursor.fetchall()
                    if self.sql_log == '1':
                        self.logger.info(
                            '(%d).结果:成功 返回值:%s 影响行:%s   SQL:%s' % (index, str(info), cursor.rowcount, self.custom_sql))
                    else:
                        self.logger.info('(%d).结果:成功 返回值:%s 影响行:%s' % (index, str(info), cursor.rowcount))
                    time.sleep(float(self.custom_sleep))
                except Exception as e:
                    self.logger.error('(%d).失败!!!%s SQL:%s' % (index, e, self.custom_sql))
                    time.sleep(float(self.error_sleep))
                    for i in range(5):
                        try:
                            db = pyoracle.connect(self.username, self.password,self.ip + ':' + self.port + '/' + self.db_name)
                            cursor = db.cursor()
                            cursor.execute(self.custom_sql)
                            cursor.execute('''select * from v$version''')
                            outinfo = cursor.fetchall()[0][0]
                            self.logger.info('重试成功!!! 数据库版本:' + outinfo)
                            break
                        except Exception as e:
                            self.logger.error(
                                '尝试第(%d)次重试失败!!! 等待重试... 等待超时时间%d秒...  %s' % (i + 1, int(self.error_sleep), str(e)))
                            time.sleep(float(self.error_sleep))
                finally:
                    index += 1


        try:
            if self.test_mode == 'insert':
                oracle_insert()

            elif self.test_mode == 'update':
                oracle_update()

            elif self.test_mode == 'delete':
                oracle_delete()

            elif self.test_mode == 'mode_iud':
                oracle_iud()

            elif self.test_mode == 'custom':
                oracle_custom()

            else:pass
        except Exception as e:
            self.logger.error('连接失败!!!%s'%e)
            time.sleep(float(self.error_sleep))

    def main(self):
        if self.database_type == 'mysql':
            self.mysql()
        elif self.database_type == 'sqlserver':
            self.sqlserver()
        elif self.database_type == 'oracle':
            self.oracle()
        else:pass
        self.logger.info('测试结束!!!')

if __name__ == '__main__':
    s_time = time.time()
    database_test = DataBase_test()
    database_test.main()
    e_time = time.time()
    input('运行时间:%d秒  回车结束!!!'%(int(e_time-s_time)))
