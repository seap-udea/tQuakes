old=$1;shift
new=$1

rm $old.html
rm $old*.png

for ext in py conf history
do
    mv $old.$ext $new.$ext
done

