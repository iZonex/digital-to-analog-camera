#!/bin/bash

# Задайте переменные
RPI_USER="zym"  # Имя пользователя на Raspberry Pi
RPI_HOST=$1  # 192.168.3.211
RPI_PATH="/home/zym"  # Путь к директории на Raspberry Pi, куда будут скопированы файлы
SETUP_FLAG_FILE="/home/zym/.setup_done"  # Путь к файлу-индикатору завершения настройки

# Копирование файлов на Raspberry Pi
scp fpv_camera.service zym@$RPI_HOST:$RPI_PATH
scp fpv_camera.py zym@$RPI_HOST:$RPI_PATH
scp rtsp_stream.service zym@$RPI_HOST:$RPI_PATH

# Установка и запуск сервиса fpv_camera и rtsp_stream через SSH
ssh -t zym@$RPI_HOST << 'EOF'
if [ ! -f $SETUP_FLAG_FILE ]; then
  # Установка rinetd в тихом режиме
  sudo apt-get update -qq
  sudo apt-get install -qq rinetd

  sudo mv /home/zym/fpv_camera.service /etc/systemd/system/
  sudo mv /home/zym/rtsp_stream.service /etc/systemd/system/
  sudo systemctl enable fpv_camera.service
  sudo systemctl enable rtsp_stream.service
  sudo systemctl daemon-reload
  sudo systemctl start fpv_camera.service
  sudo systemctl start rtsp_stream.service
  sudo systemctl restart fpv_camera.service
  sudo systemctl restart rtsp_stream.service

  sudo sed -i 's/$/ consoleblank=1 loglevel=0/' /boot/firmware/cmdline.txt
  echo 'disable_splash=1' | sudo tee -a /boot/firmware/config.txt > /dev/null

  # Добавление правил перенаправления портов с камеры в /etc/rinetd.conf
  echo '0.0.0.0 80 192.168.133.208 80' | sudo tee -a /etc/rinetd.conf > /dev/null
  echo '0.0.0.0 443 192.168.133.208 443' | sudo tee -a /etc/rinetd.conf > /dev/null
  echo '0.0.0.0 12351 192.168.133.208 12351' | sudo tee -a /etc/rinetd.conf > /dev/null
  sudo systemctl restart rinetd

  # Создание файла-индикатора, что настройка выполнена
  touch $SETUP_FLAG_FILE
fi
EOF

echo "Файлы были скопированы и сервисы запущены."
