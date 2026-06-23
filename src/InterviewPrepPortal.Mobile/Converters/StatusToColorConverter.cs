using System.Globalization;
using InterviewPrepPortal.Models;

namespace InterviewPrepPortal.Mobile.Converters;

/// <summary>Maps a ProgressStatus to the card border color used throughout the web app.</summary>
public class StatusToColorConverter : IValueConverter
{
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        return value switch
        {
            ProgressStatus.Mastered => Color.FromArgb("#10B981"),
            ProgressStatus.Learning => Color.FromArgb("#F59E0B"),
            _ => Color.FromArgb("#334155")
        };
    }

    public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture) =>
        throw new NotSupportedException();
}
