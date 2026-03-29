# Maintainer: Hicham Bouchikhi <hbouchikhi@outlook.com>
pkgname=yeti-gx-linux
pkgver=1.0.0
pkgrel=1
pkgdesc="Logitech Yeti GX hardware control for Linux (gain, mute, Smart Audio Lock)"
arch=('any')
url="https://github.com/esperadoce/yeti-gx-linux"
license=('MIT')
depends=('python')
source=("$pkgname-$pkgver.tar.gz::$url/archive/refs/heads/master.tar.gz")
sha256sums=('SKIP')

package() {
    cd "$srcdir/$pkgname-master"
    install -Dm755 yeti-ctl.py "$pkgdir/usr/bin/yeti-ctl"
    install -Dm644 udev/99-yeti-gx.rules "$pkgdir/usr/lib/udev/rules.d/99-yeti-gx.rules"
}
