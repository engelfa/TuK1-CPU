ps aux | grep -ie build/tuk_cpu | awk '{print $2}' | xargs kill -9
