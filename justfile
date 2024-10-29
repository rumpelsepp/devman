build-arch:
    cd arch && just build

build-debian:
    cd debian && just build

lint: shellcheck

shellcheck:
    shellcheck devpod
