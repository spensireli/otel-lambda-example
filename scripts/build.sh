#!/usr/bin/env bash


BASE=$(pwd)
FULL_LAMBDA_DIR="$BASE"/lib/lambda_code
BUILD_DIR=lambda_build_dir

if [ -z "$1" ]; then
  DEST="$BASE"/build
else
  DEST="$BASE"/"$1"
fi

build_lambda_fn () {
  if [ -z "$1" ]; then
    echo "build_lambda_fn requires the lambda identifier as first argument" && exit 1
  fi

  LAMBDA=$1

  LAMBDA_BUILD_DIR="$DEST"/"$BUILD_DIR"/"$LAMBDA"

  echo "Params: dest $DEST - build dir $BUILD_DIR - lambda build dir $LAMBDA_BUILD_DIR"
  echo "Building $LAMBDA"
  mkdir -p "$LAMBDA_BUILD_DIR"/lib/lambda_code/"$LAMBDA"
  cp -r "$FULL_LAMBDA_DIR"/"$LAMBDA" "$LAMBDA_BUILD_DIR"/lib/lambda_code/
  for x in $(ls -d "$BASE"/lib/*/ | grep -v -e lambda_code);
  do
    cp "$BASE/lib/config.yaml" "$LAMBDA_BUILD_DIR"/;
    cp -r "$x" "$LAMBDA_BUILD_DIR"/lib/$(basename $x)/;
    if [ -f requirements/$(basename $x).txt ]; then
      docker run --platform linux/amd64 -v "$BASE"/:/build --entrypoint "pip" public.ecr.aws/lambda/python:3.9 \
        install --compile -r /build/requirements/$(basename $x).txt -t /build/build/lambda_build_dir/$LAMBDA
    fi
  done
  cd "$LAMBDA_BUILD_DIR"/lib/lambda_code/"$LAMBDA" || exit 1
  cd - > /dev/null || exit 1
  if [ -f requirements/"$LAMBDA".txt ]; then
    docker run --platform linux/amd64 -v "$BASE"/:/build --entrypoint "pip" public.ecr.aws/lambda/python:3.9 \
      install --compile -r /build/requirements/$LAMBDA.txt -t /build/build/lambda_build_dir/$LAMBDA
  else
    cp -r "$DEST"/"$BUILD_DIR"/common/ "$LAMBDA_BUILD_DIR"/lib/lambda_code/"$LAMBDA"

  fi
  mkdir "$LAMBDA_BUILD_DIR"/vendor
  cp "$BASE/lib/config.yaml" "$LAMBDA_BUILD_DIR"/;
  cd "$LAMBDA_BUILD_DIR" || (echo "Could not cd to $LAMBDA_BUILD_DIR" && exit 1)
  echo "Lambda - $LAMBDA"
  echo "Zipping: $(pwd)" && zip -Drq ../../"$LAMBDA".zip ./* || \
    (echo "Failed to zip $DEST/$BUILD_DIR/$LAMBDA" && exit 1)
}

common_install_fn () {
  echo "Running common install"
  pip3 install -U pip
  mkdir -p "$DEST"/"$BUILD_DIR"/common/
  pip3 cache purge
  pip3 install --no-cache --compile -r requirements/common.txt -t "$DEST"/"$BUILD_DIR"/common/
}

rm -r "$DEST"

BUILD_DIR=lambda_build_dir
if [ ! -d "$DEST/$BUILD_DIR" ]; then
  mkdir -p "$DEST"/$BUILD_DIR
fi

echo Dest: "$DEST" -  Build dir: "$BUILD_DIR"
common_install_fn

declare -a pids
for LAMBDA in $(ls "$FULL_LAMBDA_DIR" | grep -v .py ); do
  build_lambda_fn "$LAMBDA" &
  pids+=("$!")
done

for pid in "${pids[@]}"; do
  echo "WAITING on $pid"
  wait "$pid"
done

rm -r "${DEST:?}/$BUILD_DIR"
