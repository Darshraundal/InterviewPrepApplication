namespace InterviewPrepPortal.Mobile.Services;

/// <summary>
/// Bundled JSON content (Resources/Raw/jsondata/**) is packaged inside the APK and
/// can only be read through FileSystem.OpenAppPackageFileAsync, not via normal
/// File/Directory APIs. QuestionService/ProjectGuideService need a real folder on
/// disk to glob over, so on first launch (or after an app update) we extract every
/// file listed in jsondata/manifest.txt into app-local storage.
/// </summary>
public static class JsonDataSeeder
{
    private const string ManifestLogicalName = "jsondata/manifest.txt";
    private const string VersionMarkerFileName = ".seeded-version";

    public static async Task EnsureSeededAsync()
    {
        var targetRoot = new MobileJsonDataLocator().JsonDataRoot;
        var markerPath = Path.Combine(targetRoot, VersionMarkerFileName);
        var currentVersion = AppInfo.Current.VersionString + "+" + AppInfo.Current.BuildString;

        if (File.Exists(markerPath) && await File.ReadAllTextAsync(markerPath) == currentVersion)
        {
            return; // already extracted for this app version
        }

        Directory.CreateDirectory(targetRoot);

        var relativePaths = await ReadManifestAsync();
        foreach (var relativePath in relativePaths)
        {
            var logicalName = "jsondata/" + relativePath;
            var destinationPath = Path.Combine(targetRoot, relativePath.Replace('/', Path.DirectorySeparatorChar));

            Directory.CreateDirectory(Path.GetDirectoryName(destinationPath)!);

            using var sourceStream = await FileSystem.OpenAppPackageFileAsync(logicalName);
            using var destinationStream = File.Create(destinationPath);
            await sourceStream.CopyToAsync(destinationStream);
        }

        await File.WriteAllTextAsync(markerPath, currentVersion);
    }

    private static async Task<List<string>> ReadManifestAsync()
    {
        using var stream = await FileSystem.OpenAppPackageFileAsync(ManifestLogicalName);
        using var reader = new StreamReader(stream);

        var lines = new List<string>();
        string? line;
        while ((line = await reader.ReadLineAsync()) != null)
        {
            if (!string.IsNullOrWhiteSpace(line))
                lines.Add(line.Trim());
        }

        return lines;
    }
}
