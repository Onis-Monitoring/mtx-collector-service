echo "Collecting MEfs from AT&T SFTP..."

bash collect_mefs.bash "$1" "$2" "$3" > mefs.log

echo "Detecting GTC Gaps..."

python detect_gtc_gaps.py