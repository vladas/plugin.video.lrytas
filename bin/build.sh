#!/usr/bin/php
<?php

$basePath = __DIR__ . '/..';

$addonXml = simplexml_load_file($basePath . '/plugin/addon.xml');

$attribs = array();
foreach ($addonXml->attributes() as $key => $val) {
    $attribs[$key] = $val;
}

$pluginId = $attribs['id'];
$version = $attribs['version'];


$zip = new ZipArchive();

$filename = realpath($basePath) . "/$pluginId-$version.zip";

echo $filename, "\n";

if (file_exists($filename)) {
    unlink($filename);
}

if ($zip->open($filename, ZIPARCHIVE::CREATE)!==TRUE) {
    exit("cannot open <$filename>\n");
}

if (!$zip->addEmptyDir($pluginId)) {
    exit("cannot add dir <$pluginId>\n");
}


$source = realpath($basePath . '/plugin');

if (is_dir($source) === true) {
    $files = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($source), RecursiveIteratorIterator::LEAVES_ONLY);
    foreach ($files as $file) {
        $file = str_replace('\\', '/', $file);
        $fileName = substr($file, strrpos($file, '/') + 1);

        // Ignore system files, "." and ".." folders
        if ($fileName{0} == '.') {
            continue;
        }

        $file = realpath($file);

        if (is_dir($file) === true) {
            $zip->addEmptyDir($pluginId . '/' . str_replace($source . '/', '', $file . '/'));
        } elseif (is_file($file) === true) {
        	$zip->addFromString($pluginId . '/' . str_replace($source . '/', '', $file), file_get_contents($file));
        }
    }
} elseif (is_file($source) === true) {
    $zip->addFromString(basename($source), file_get_contents($source));
}

$zip->close();