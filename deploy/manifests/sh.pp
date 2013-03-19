Exec { path => [ "/bin/", "/sbin/", "/usr/bin/", "/usr/sbin/", "/usr/local/bin/" ] }

define line($file, $line, $ensure = 'present') {
    case $ensure {
        default : { err ( "unknown ensure value ${ensure}" ) }
        present: {
            exec { "/bin/echo '${line}' >> '${file}'":
                unless => "/bin/grep -qFx '${line}' '${file}'"
            }
        }
        absent: {
            exec { "/bin/grep -vFx '${line}' '${file}' | /usr/bin/tee '${file}' > /dev/null 2>&1":
              onlyif => "/bin/grep -qFx '${line}' '${file}'"
            }

            # Use this resource instead if your platform's grep doesn't support -vFx;
            # note that this command has been known to have problems with lines containing quotes.
            # exec { "/usr/bin/perl -ni -e 'print unless /^\\Q${line}\\E\$/' '${file}'":
            #     onlyif => "/bin/grep -qFx '${line}' '${file}'"
            # }
        }
    }
}


class smarthouse {
    user { 'aiko':
        ensure => present,
        managehome => true,
        groups => 'admin',
        shell => '/bin/bash',
        require => Group['admin'],
    }

    group { 'admin':
        ensure => present,
    }

    package {'git':
        ensure => installed,
    }

    exec { 'repo':
        command => "sudo -u aiko git clone git://github.com/antigluk/pySmartHouse.git",
        cwd     => "/home/aiko",
        require => [User['aiko'], Package['git']],
        onlyif => "test ! -d /home/aiko/pySmartHouse",
    }

    exec { 'submodules':
        command => "sudo -u aiko git submodule update --init",
        cwd     => "/home/aiko/pySmartHouse",
        require => Exec['repo'],
    }

    exec { 'aiko-pass':
        command => "sudo passwd aiko << EOF\naiko\naiko\nEOF",
        onlyif => "egrep -q '^aiko:*:' /etc/shadow",
        require => User[aiko],
    }

    exec { 'github-keys':
        command => "cp -r /vagrant/ssh /home/aiko/.ssh && chown aiko:aiko -R /home/aiko/.ssh",
        onlyif => "test -d ",
        require => User[aiko],
    }


    include frontend
}

class frontend {
    include smarthouse

    file { '/home/aiko/frontend':
        ensure => link,
        target => '/home/aiko/pySmartHouse/web-frontend',
        require => Class['smarthouse'],
    }

    package { 'python-pip':
        ensure => installed,
    }

    exec {'virtualenv':
        command => 'pip install virtualenv',
        require => package['python-pip'],
    }

    exec {'env':
        command => 'virtualenv /home/aiko/pySmartHouse/web-frontend/.env',
        require => Exec['virtualenv'],
        onlyif => 'test ! -d /home/aiko/pySmartHouse/web-frontend/.env',
    }

    exec {'pip install':
        command => '/home/aiko/pySmartHouse/web-frontend/.env/bin/pip install flask sh',
        require => Exec['env'],
    }

    exec {'sqlite3dbm':
        command => '/home/aiko/pySmartHouse/web-frontend/.env/bin/pip install -e /home/aiko/pySmartHouse/3rdparty/sqlite3dbm',
        require => [Exec['env'], Class['smarthouse']],
    }

}

include frontend