import paramiko
import os
from tqdm import tqdm
import time
import re

class RemoteSync:
    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.ssh = None
        self.sftp = None
    
    def sanitize_filename(self, filename):
        """处理文件名中的特殊字符"""
        # 替换不安全的字符为下划线
        safe_name = re.sub(r'[\\/*?:"<>|\']', '_', filename)
        return safe_name
    
    def connect(self):
        """建立SSH连接"""
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password
            )
            self.sftp = self.ssh.open_sftp()
            print("SSH连接成功")
        except Exception as e:
            print(f"SSH连接失败: {str(e)}")
            raise
    
    def download_folder(self, remote_path, local_path):
        """下载远程文件夹到本地"""
        try:
            # 确保本地文件夹存在
            os.makedirs(local_path, exist_ok=True)
            
            # 列出远程文件夹内容
            files = self.sftp.listdir(remote_path)
            
            # 使用tqdm显示进度
            with tqdm(files) as pbar:
                for filename in pbar:
                    remote_file = f"{remote_path}/{filename}"
                    # 处理文件名中的特殊字符
                    safe_filename = self.sanitize_filename(filename)
                    local_file = os.path.join(local_path, safe_filename)
                    
                    try:
                        # 更新进度条描述
                        pbar.set_description(f"下载: {filename}")
                        
                        # 获取远程文件属性
                        file_attr = self.sftp.stat(remote_file)
                        
                        # 检查是否为目录
                        if file_attr.st_mode & 0o40000:  # 检查是否为目录
                            # 递归下载子目录
                            os.makedirs(local_file, exist_ok=True)
                            self.download_folder(remote_file, local_file)
                        else:
                            # 下载文件，添加重试机制
                            for attempt in range(3):  # 最多重试3次
                                try:
                                    self.sftp.get(remote_file, local_file)
                                    break
                                except Exception as e:
                                    if attempt == 2:  # 最后一次尝试
                                        raise
                                    time.sleep(1)  # 等待1秒后重试
                        
                    except Exception as e:
                        print(f"下载文件 {filename} 失败: {str(e)}")
                        continue
            
            print(f"文件夹同步完成: {remote_path} -> {local_path}")
            
        except Exception as e:
            print(f"下载文件夹失败: {str(e)}")
            raise
        
    def close(self):
        """关闭连接"""
        if self.sftp:
            self.sftp.close()
        if self.ssh:
            self.ssh.close()

def main():
    # SSH连接配置
    config = {
        'hostname': 'connect.westb.seetacloud.com',
        'port': 48118,
        'username': 'root',
        'password': 'ZZSHMxJ7+NzJ'
    }
    
    # 远程和本地路径
    remote_path = '/root/autodl-tmp/ComfyUI/output/char_batch_face3'
    local_path = 'static/character_images_face'
    
    # 创建同步器实例
    syncer = RemoteSync(**config)
    
    try:
        # 连接到服务器
        syncer.connect()
        
        # 下载文件夹
        syncer.download_folder(remote_path, local_path)
        
    except Exception as e:
        print(f"同步过程出错: {str(e)}")
        
    finally:
        # 确保关闭连接
        syncer.close()

if __name__ == "__main__":
    main() 