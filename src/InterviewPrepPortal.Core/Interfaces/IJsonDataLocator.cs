namespace InterviewPrepPortal.Interfaces;

/// <summary>
/// Resolves the on-disk root folder that contains categories.json, questions-*.json
/// and the projects/ subfolder. The web app points this at wwwroot-adjacent
/// Data/JsonData; the mobile app points it at a folder under app-local storage
/// that the bundled JSON assets are extracted to on first launch.
/// </summary>
public interface IJsonDataLocator
{
    string JsonDataRoot { get; }
}
