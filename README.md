# pandas-flowchart 📊

A Python library that integrates with pandas to automatically track data transformation operations and generate visual flowcharts using HTML or Mermaid diagrams.

## Features

- **Automatic Operation Tracking**: Intercepts common pandas operations (merge, filter, assign, drop, groupby, etc.)
- **Structured Metadata Recording**: Captures operation details, row counts, and custom statistics
- **Visual Flowcharts**: Generates Mermaid diagrams with color-coded operation boxes
- **Variable Monitoring**: Track specific variables' unique counts and statistics across the pipeline
- **Mini-Histograms**: ASCII sparkline histograms for numeric variables
- **Multiple Output Formats**: Export to Markdown, HTML, or raw Mermaid syntax

## Example: Healthcare Data Pipeline

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Example: Healthcare Data Pipeline</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: #ffffff;
            color: #333333;
            min-height: 100vh;
            padding: 2rem;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            margin-bottom: 2rem;
            font-weight: 300;
            font-size: 2rem;
            letter-spacing: 0.05em;
        }
        .mermaid {
            display: flex;
            justify-content: center;
            background: #ffffff;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .footer {
            text-align: center;
            margin-top: 2rem;
            font-size: 0.875rem;
            opacity: 0.7;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Example: Healthcare Data Pipeline</h1>
        <div class="mermaid">
flowchart TB

    %% Node definitions
    op_1[/"`<b>`Load Patients`</b><br/>``<i>`Load patients data from warehouse`</i><br/>`⬅️ 5,000 rows × 6 cols`<br/>`────────────────────`<br/>`🔑 patient_id: 5,000 unique`<br/>`⭐ age: 82 unique`<br/>`mean=54.95 [14.0–95.0]`<br/><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGUAAAAoCAYAAADnujR9AAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjcsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvTLEjVAAAAAlwSFlzAAAMTgAADE4Bf3eMIwAABIFJREFUeJzt2luoFVUcx/GPxyNZahesCLOgmi4PBpWcsKLIDJNuVCRoWGTGbIqgeugG+VYUEdEd9lQahdVDl4d6MqL7je2lG2p5skJT85Km4iUvp4f/7DzY3uccPft0tjpfWOw9M/8185/1W+u/1sz8B3R0dChoLlr724FG0FZub8VN+KhSSpb0tz+9paW/HegtuSCv4iV831Zun9LPLvWaAftz+MoFeQWTsQAjcTheR6lSSjb2o3s1aSu3j8a8Simp2/D7rSht5faBQpAbMB/P4G/chzPxCyZWSsncTnVaMQaXYTTewKtdNVAD/R2Eh3Av7qqUkqfq2XYpSlu5vQVv5WXW/+F8T8gFeRlThCDPYnUnk+uFWDAdfwohLhUjqTNv49ZKKVnXh/6eLEbvufgZd1dKybv17LsT5TR8geH4GrdVSsn8hnr832u24EJchXWYh/mVUrIyPz4QM3EjvhEjZHWNU50qRs2x+fYu/IpFItT9imk4GyswuVJKPu6D+5mEsugM7+MDfFApJXPq1ek2fLWV20/FDFyADjGhPlApJWtr2A7FKAzGDmzPf6v/12BNpZTs2qPeABFOJmMSRtRw5Q8h0ECMx7d4Wm1BqgzGNdgqBFwuQlxnrsBUDMJjmF4pJdvzcHMWzsP5IiR+md//V91FjbZy+xDRYaZiPWbhQxyNub0V5RhMxCG4HUl+kQfRLnpatSQY0OUJQ5wV+D0vazEurwurREiaK3p3ghPyMkIs478Tgqzq5lo9ZSTux4n4QYS7NhyaH+8Q93xUvv0TXhTzUXUEt+IMu9viapyC78Xc92Ned4QGirI03zVehI4j9jD9QzTyUmwTy+0W0bNbRGMOy+sdmf8OEyKuF0LMET263qppsGjAldjUpeN7TytuESNnmwhvS8SCYYEYkSdhgpgbhmAnPsrv5UzRcatsxmy8iQ2d9ncryr48PM7GJ7hONPZSLBbxf8tenKdVNPJwIcoG0SO7YqsYnX3BDmRiQm4Rou/cw2ZhXgZhLC7Jy0YxgS/LyxL8lu/fZS/Z1yf6rXhtH+tW2SFuvNE9vrf05Nlmu+ics3GYGO1b7IMAtTggXrP0M5sbfcL9/jXLgUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShPS01f3A8VXwoLeM7g7g56IslV8Ej2kO8OCHrFMfKWtS81v9FmW3YlrRfZIQd9yDt5J03R3cl5HR0fNUi6Xl9U7VpTGlVrt3NVE/0Sf95ECarTzfptLfCDz70SfZdkokXe7UKg3A39hcZqmj/aPewceWZaNE1mT20T67ZMi321Wmqaf0uk5JU3TH0TuLRyHz9I0nSay/AoaxzW4A4+LnLFNYpm8vGpQb05ZhnFZln2Iz/vWx4OO5/CIyJs+Pk3Ti3GPSJtFfVEux4w0Tcfioj528qAiTdNFaZrehvdEZikxTQyq2nSeU0biYZwuHhavzLJsQqeKBQ0gy7IxuFmErJlZlr2AoXi+alOsvpqQ4oVkE/IP4LOFthHjbwgAAAAASUVORK5CYII=" alt="age distribution" style="width:80px;height:25px;vertical-align:middle;" />``<br/>`top: 94:1%, 92:1%"/]
    op_2[/"`<b>`Load Visits`</b><br/>``<i>`Load visits data from warehouse`</i><br/>`⬅️ 15,000 rows × 7 cols`<br/>`────────────────────`<br/>`🔑 patient_id: 4,768 unique`<br/>`🔑 visit_id: 15,000 unique`<br/>`🔑 department: 6 unique"/]
    op_3[/"`<b>`Load Labs`</b><br/>``<i>`Load labs data from warehouse`</i><br/>`⬅️ 25,000 rows × 6 cols`<br/>`────────────────────`<br/>`🔑 visit_id: 12,207 unique"/]
    op_4[/"`<b>`Load Diagnoses`</b><br/>``<i>`Load diagnoses data from warehouse`</i><br/>`⬅️ 20,000 rows × 5 cols`<br/>`────────────────────`<br/>`🔑 visit_id: 11,005 unique"/]
    op_5[["`<b>`Merge (inner)`</b><br/>``<i>`INNER join on patient_id`</i><br/>`➡️ patients: 5,000×6`<br/>`➡️ visits: 15,000×7`<br/>`⬅️ 15,000 rows × 12 cols`<br/>`↑ +10,000 (+200.0%)`<br/>`────────────────────`<br/>`🔑 patient_id: 4,768 unique`<br/>`🔑 visit_id: 15,000 unique`<br/>`🔑 department: 6 unique`<br/>`⭐ age: 82 unique`<br/>`mean=55.02 [14.0–95.0]`<br/><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGUAAAAoCAYAAADnujR9AAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjcsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvTLEjVAAAAAlwSFlzAAAMTgAADE4Bf3eMIwAABIFJREFUeJzt2luoFVUcx/GPxyNZahesCLOgmi4PBpWcsKLIDJNuVCRoWGTGbIqgeugG+VYUEdEd9lQahdVDl4d6MqL7je2lG2p5skJT85Km4iUvp4f/7DzY3uccPft0tjpfWOw9M/8185/1W+u/1sz8B3R0dChoLlr724FG0FZub8VN+KhSSpb0tz+9paW/HegtuSCv4iV831Zun9LPLvWaAftz+MoFeQWTsQAjcTheR6lSSjb2o3s1aSu3j8a8Simp2/D7rSht5faBQpAbMB/P4G/chzPxCyZWSsncTnVaMQaXYTTewKtdNVAD/R2Eh3Av7qqUkqfq2XYpSlu5vQVv5WXW/+F8T8gFeRlThCDPYnUnk+uFWDAdfwohLhUjqTNv49ZKKVnXh/6eLEbvufgZd1dKybv17LsT5TR8geH4GrdVSsn8hnr832u24EJchXWYh/mVUrIyPz4QM3EjvhEjZHWNU50qRs2x+fYu/IpFItT9imk4GyswuVJKPu6D+5mEsugM7+MDfFApJXPq1ek2fLWV20/FDFyADjGhPlApJWtr2A7FKAzGDmzPf6v/12BNpZTs2qPeABFOJmMSRtRw5Q8h0ECMx7d4Wm1BqgzGNdgqBFwuQlxnrsBUDMJjmF4pJdvzcHMWzsP5IiR+md//V91FjbZy+xDRYaZiPWbhQxyNub0V5RhMxCG4HUl+kQfRLnpatSQY0OUJQ5wV+D0vazEurwurREiaK3p3ghPyMkIs478Tgqzq5lo9ZSTux4n4QYS7NhyaH+8Q93xUvv0TXhTzUXUEt+IMu9viapyC78Xc92Ned4QGirI03zVehI4j9jD9QzTyUmwTy+0W0bNbRGMOy+sdmf8OEyKuF0LMET263qppsGjAldjUpeN7TytuESNnmwhvS8SCYYEYkSdhgpgbhmAnPsrv5UzRcatsxmy8iQ2d9ncryr48PM7GJ7hONPZSLBbxf8tenKdVNPJwIcoG0SO7YqsYnX3BDmRiQm4Rou/cw2ZhXgZhLC7Jy0YxgS/LyxL8lu/fZS/Z1yf6rXhtH+tW2SFuvNE9vrf05Nlmu+ics3GYGO1b7IMAtTggXrP0M5sbfcL9/jXLgUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShPS01f3A8VXwoLeM7g7g56IslV8Ej2kO8OCHrFMfKWtS81v9FmW3YlrRfZIQd9yDt5J03R3cl5HR0fNUi6Xl9U7VpTGlVrt3NVE/0Sf95ECarTzfptLfCDz70SfZdkokXe7UKg3A39hcZqmj/aPewceWZaNE1mT20T67ZMi321Wmqaf0uk5JU3TH0TuLRyHz9I0nSay/AoaxzW4A4+LnLFNYpm8vGpQb05ZhnFZln2Iz/vWx4OO5/CIyJs+Pk3Ti3GPSJtFfVEux4w0Tcfioj528qAiTdNFaZrehvdEZikxTQyq2nSeU0biYZwuHhavzLJsQqeKBQ0gy7IxuFmErJlZlr2AoXi+alOsvpqQ4oVkE/IP4LOFthHjbwgAAAAASUVORK5CYII=" alt="age distribution" style="width:80px;height:25px;vertical-align:middle;" />``<br/>`top: 56:1%, 41:1%"]]
    op_6{"`<b>`Query`</b><br/>``<i>`Filter: visit_date &gt;= &#x27;2024-01-01&#x27;`</i><br/>`➡️ df_1: 15,000×12`<br/>`⬅️ 7,500 rows × 12 cols`<br/>`↓ -7,500 (-50.0%)`<br/>`────────────────────`<br/>`🔑 patient_id: 3,899 unique`<br/>`🔑 visit_id: 7,500 unique`<br/>`🔑 department: 6 unique`<br/>`⭐ age: 82 unique`<br/>`mean=54.74 [14.0–95.0]`<br/><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGUAAAAoCAYAAADnujR9AAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjcsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvTLEjVAAAAAlwSFlzAAAMTgAADE4Bf3eMIwAABIFJREFUeJzt2luoFVUcx/GPxyNZahesCLOgmi4PBpWcsKLIDJNuVCRoWGTGbIqgeugG+VYUEdEd9lQahdVDl4d6MqL7je2lG2p5skJT85Km4iUvp4f/7DzY3uccPft0tjpfWOw9M/8185/1W+u/1sz8B3R0dChoLlr724FG0FZub8VN+KhSSpb0tz+9paW/HegtuSCv4iV831Zun9LPLvWaAftz+MoFeQWTsQAjcTheR6lSSjb2o3s1aSu3j8a8Simp2/D7rSht5faBQpAbMB/P4G/chzPxCyZWSsncTnVaMQaXYTTewKtdNVAD/R2Eh3Av7qqUkqfq2XYpSlu5vQVv5WXW/+F8T8gFeRlThCDPYnUnk+uFWDAdfwohLhUjqTNv49ZKKVnXh/6eLEbvufgZd1dKybv17LsT5TR8geH4GrdVSsn8hnr832u24EJchXWYh/mVUrIyPz4QM3EjvhEjZHWNU50qRs2x+fYu/IpFItT9imk4GyswuVJKPu6D+5mEsugM7+MDfFApJXPq1ek2fLWV20/FDFyADjGhPlApJWtr2A7FKAzGDmzPf6v/12BNpZTs2qPeABFOJmMSRtRw5Q8h0ECMx7d4Wm1BqgzGNdgqBFwuQlxnrsBUDMJjmF4pJdvzcHMWzsP5IiR+md//V91FjbZy+xDRYaZiPWbhQxyNub0V5RhMxCG4HUl+kQfRLnpatSQY0OUJQ5wV+D0vazEurwurREiaK3p3ghPyMkIs478Tgqzq5lo9ZSTux4n4QYS7NhyaH+8Q93xUvv0TXhTzUXUEt+IMu9viapyC78Xc92Ned4QGirI03zVehI4j9jD9QzTyUmwTy+0W0bNbRGMOy+sdmf8OEyKuF0LMET263qppsGjAldjUpeN7TytuESNnmwhvS8SCYYEYkSdhgpgbhmAnPsrv5UzRcatsxmy8iQ2d9ncryr48PM7GJ7hONPZSLBbxf8tenKdVNPJwIcoG0SO7YqsYnX3BDmRiQm4Rou/cw2ZhXgZhLC7Jy0YxgS/LyxL8lu/fZS/Z1yf6rXhtH+tW2SFuvNE9vrf05Nlmu+ics3GYGO1b7IMAtTggXrP0M5sbfcL9/jXLgUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShPS01f3A8VXwoLeM7g7g56IslV8Ej2kO8OCHrFMfKWtS81v9FmW3YlrRfZIQd9yDt5J03R3cl5HR0fNUi6Xl9U7VpTGlVrt3NVE/0Sf95ECarTzfptLfCDz70SfZdkokXe7UKg3A39hcZqmj/aPewceWZaNE1mT20T67ZMi321Wmqaf0uk5JU3TH0TuLRyHz9I0nSay/AoaxzW4A4+LnLFNYpm8vGpQb05ZhnFZln2Iz/vWx4OO5/CIyJs+Pk3Ti3GPSJtFfVEux4w0Tcfioj528qAiTdNFaZrehvdEZikxTQyq2nSeU0biYZwuHhavzLJsQqeKBQ0gy7IxuFmErJlZlr2AoXi+alOsvpqQ4oVkE/IP4LOFthHjbwgAAAAASUVORK5CYII=" alt="age distribution" style="width:80px;height:25px;vertical-align:middle;" />``<br/>`top: 31:1%, 56:1%"}
    op_6_removed[/"🗑️ Removed`<br/>`7,500 rows`<br/>`(50.0%)"/]
    op_7{"`<b>`Query`</b><br/>``<i>`Filter: age &gt;= 18`</i><br/>`➡️ df_1: 7,500×12`<br/>`⬅️ 7,199 rows × 12 cols`<br/>`↓ -301 (-4.0%)`<br/>`────────────────────`<br/>`🔑 patient_id: 3,749 unique`<br/>`🔑 visit_id: 7,199 unique`<br/>`🔑 department: 6 unique`<br/>`⭐ age: 78 unique`<br/>`mean=56.36 [18.0–95.0]`<br/><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGUAAAAoCAYAAADnujR9AAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjcsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvTLEjVAAAAAlwSFlzAAAMTgAADE4Bf3eMIwAABIFJREFUeJzt2luoFVUcx/GPxyNZahesCLOgmi4PBpWcsKLIDJNuVCRoWGTGbIqgeugG+VYUEdEd9lQahdVDl4d6MqL7je2lG2p5skJT85Km4iUvp4f/7DzY3uccPft0tjpfWOw9M/8185/1W+u/1sz8B3R0dChoLlr724FG0FZub8VN+KhSSpb0tz+9paW/HegtuSCv4iV831Zun9LPLvWaAftz+MoFeQWTsQAjcTheR6lSSjb2o3s1aSu3j8a8Simp2/D7rSht5faBQpAbMB/P4G/chzPxCyZWSsncTnVaMQaXYTTewKtdNVAD/R2Eh3Av7qqUkqfq2XYpSlu5vQVv5WXW/+F8T8gFeRlThCDPYnUnk+uFWDAdfwohLhUjqTNv49ZKKVnXh/6eLEbvufgZd1dKybv17LsT5TR8geH4GrdVSsn8hnr832u24EJchXWYh/mVUrIyPz4QM3EjvhEjZHWNU50qRs2x+fYu/IpFItT9imk4GyswuVJKPu6D+5mEsugM7+MDfFApJXPq1ek2fLWV20/FDFyADjGhPlApJWtr2A7FKAzGDmzPf6v/12BNpZTs2qPeABFOJmMSRtRw5Q8h0ECMx7d4Wm1BqgzGNdgqBFwuQlxnrsBUDMJjmF4pJdvzcHMWzsP5IiR+md//V91FjbZy+xDRYaZiPWbhQxyNub0V5RhMxCG4HUl+kQfRLnpatSQY0OUJQ5wV+D0vazEurwurREiaK3p3ghPyMkIs478Tgqzq5lo9ZSTux4n4QYS7NhyaH+8Q93xUvv0TXhTzUXUEt+IMu9viapyC78Xc92Ned4QGirI03zVehI4j9jD9QzTyUmwTy+0W0bNbRGMOy+sdmf8OEyKuF0LMET263qppsGjAldjUpeN7TytuESNnmwhvS8SCYYEYkSdhgpgbhmAnPsrv5UzRcatsxmy8iQ2d9ncryr48PM7GJ7hONPZSLBbxf8tenKdVNPJwIcoG0SO7YqsYnX3BDmRiQm4Rou/cw2ZhXgZhLC7Jy0YxgS/LyxL8lu/fZS/Z1yf6rXhtH+tW2SFuvNE9vrf05Nlmu+ics3GYGO1b7IMAtTggXrP0M5sbfcL9/jXLgUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShPS01f3A8VXwoLeM7g7g56IslV8Ej2kO8OCHrFMfKWtS81v9FmW3YlrRfZIQd9yDt5J03R3cl5HR0fNUi6Xl9U7VpTGlVrt3NVE/0Sf95ECarTzfptLfCDz70SfZdkokXe7UKg3A39hcZqmj/aPewceWZaNE1mT20T67ZMi321Wmqaf0uk5JU3TH0TuLRyHz9I0nSay/AoaxzW4A4+LnLFNYpm8vGpQb05ZhnFZln2Iz/vWx4OO5/CIyJs+Pk3Ti3GPSJtFfVEux4w0Tcfioj528qAiTdNFaZrehvdEZikxTQyq2nSeU0biYZwuHhavzLJsQqeKBQ0gy7IxuFmErJlZlr2AoXi+alOsvpqQ4oVkE/IP4LOFthHjbwgAAAAASUVORK5CYII=" alt="age distribution" style="width:80px;height:25px;vertical-align:middle;" />``<br/>`top: 31:2%, 56:2%"}
    op_7_removed[/"🗑️ Removed`<br/>`301 rows`<br/>`(4.0%)"/]
    op_8[["`<b>`Merge (left)`</b><br/>``<i>`LEFT join on visit_id`</i><br/>`➡️ df_1: 7,199×12`<br/>`➡️ labs: 25,000×6`<br/>`⬅️ 13,343 rows × 17 cols`<br/>`↑ +6,144 (+85.3%)`<br/>`────────────────────`<br/>`🔑 patient_id: 3,749 unique`<br/>`🔑 visit_id: 7,199 unique`<br/>`🔑 department: 6 unique`<br/>`⭐ age: 78 unique`<br/>`mean=56.41 [18.0–95.0]`<br/><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGUAAAAoCAYAAADnujR9AAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjcsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvTLEjVAAAAAlwSFlzAAAMTgAADE4Bf3eMIwAABIFJREFUeJzt2luoFVUcx/GPxyNZahesCLOgmi4PBpWcsKLIDJNuVCRoWGTGbIqgeugG+VYUEdEd9lQahdVDl4d6MqL7je2lG2p5skJT85Km4iUvp4f/7DzY3uccPft0tjpfWOw9M/8185/1W+u/1sz8B3R0dChoLlr724FG0FZub8VN+KhSSpb0tz+9paW/HegtuSCv4iV831Zun9LPLvWaAftz+MoFeQWTsQAjcTheR6lSSjb2o3s1aSu3j8a8Simp2/D7rSht5faBQpAbMB/P4G/chzPxCyZWSsncTnVaMQaXYTTewKtdNVAD/R2Eh3Av7qqUkqfq2XYpSlu5vQVv5WXW/+F8T8gFeRlThCDPYnUnk+uFWDAdfwohLhUjqTNv49ZKKVnXh/6eLEbvufgZd1dKybv17LsT5TR8geH4GrdVSsn8hnr832u24EJchXWYh/mVUrIyPz4QM3EjvhEjZHWNU50qRs2x+fYu/IpFItT9imk4GyswuVJKPu6D+5mEsugM7+MDfFApJXPq1ek2fLWV20/FDFyADjGhPlApJWtr2A7FKAzGDmzPf6v/12BNpZTs2qPeABFOJmMSRtRw5Q8h0ECMx7d4Wm1BqgzGNdgqBFwuQlxnrsBUDMJjmF4pJdvzcHMWzsP5IiR+md//V91FjbZy+xDRYaZiPWbhQxyNub0V5RhMxCG4HUl+kQfRLnpatSQY0OUJQ5wV+D0vazEurwurREiaK3p3ghPyMkIs478Tgqzq5lo9ZSTux4n4QYS7NhyaH+8Q93xUvv0TXhTzUXUEt+IMu9viapyC78Xc92Ned4QGirI03zVehI4j9jD9QzTyUmwTy+0W0bNbRGMOy+sdmf8OEyKuF0LMET263qppsGjAldjUpeN7TytuESNnmwhvS8SCYYEYkSdhgpgbhmAnPsrv5UzRcatsxmy8iQ2d9ncryr48PM7GJ7hONPZSLBbxf8tenKdVNPJwIcoG0SO7YqsYnX3BDmRiQm4Rou/cw2ZhXgZhLC7Jy0YxgS/LyxL8lu/fZS/Z1yf6rXhtH+tW2SFuvNE9vrf05Nlmu+ics3GYGO1b7IMAtTggXrP0M5sbfcL9/jXLgUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShPS01f3A8VXwoLeM7g7g56IslV8Ej2kO8OCHrFMfKWtS81v9FmW3YlrRfZIQd9yDt5J03R3cl5HR0fNUi6Xl9U7VpTGlVrt3NVE/0Sf95ECarTzfptLfCDz70SfZdkokXe7UKg3A39hcZqmj/aPewceWZaNE1mT20T67ZMi321Wmqaf0uk5JU3TH0TuLRyHz9I0nSay/AoaxzW4A4+LnLFNYpm8vGpQb05ZhnFZln2Iz/vWx4OO5/CIyJs+Pk3Ti3GPSJtFfVEux4w0Tcfioj528qAiTdNFaZrehvdEZikxTQyq2nSeU0biYZwuHhavzLJsQqeKBQ0gy7IxuFmErJlZlr2AoXi+alOsvpqQ4oVkE/IP4LOFthHjbwgAAAAASUVORK5CYII=" alt="age distribution" style="width:80px;height:25px;vertical-align:middle;" />``<br/>`top: 69:2%, 81:2%"]]
    op_9[["`<b>`Merge (left)`</b><br/>``<i>`LEFT join on visit_id`</i><br/>`➡️ df_1: 13,343×17`<br/>`➡️ diagnoses: 20,000×5`<br/>`⬅️ 21,280 rows × 21 cols`<br/>`↑ +7,937 (+59.5%)`<br/>`────────────────────`<br/>`🔑 patient_id: 3,749 unique`<br/>`🔑 visit_id: 7,199 unique`<br/>`🔑 department: 6 unique`<br/>`⭐ age: 78 unique`<br/>`mean=56.52 [18.0–95.0]`<br/><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGUAAAAoCAYAAADnujR9AAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjcsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvTLEjVAAAAAlwSFlzAAAMTgAADE4Bf3eMIwAABIFJREFUeJzt2luoFVUcx/GPxyNZahesCLOgmi4PBpWcsKLIDJNuVCRoWGTGbIqgeugG+VYUEdEd9lQahdVDl4d6MqL7je2lG2p5skJT85Km4iUvp4f/7DzY3uccPft0tjpfWOw9M/8185/1W+u/1sz8B3R0dChoLlr724FG0FZub8VN+KhSSpb0tz+9paW/HegtuSCv4iV831Zun9LPLvWaAftz+MoFeQWTsQAjcTheR6lSSjb2o3s1aSu3j8a8Simp2/D7rSht5faBQpAbMB/P4G/chzPxCyZWSsncTnVaMQaXYTTewKtdNVAD/R2Eh3Av7qqUkqfq2XYpSlu5vQVv5WXW/+F8T8gFeRlThCDPYnUnk+uFWDAdfwohLhUjqTNv49ZKKVnXh/6eLEbvufgZd1dKybv17LsT5TR8geH4GrdVSsn8hnr832u24EJchXWYh/mVUrIyPz4QM3EjvhEjZHWNU50qRs2x+fYu/IpFItT9imk4GyswuVJKPu6D+5mEsugM7+MDfFApJXPq1ek2fLWV20/FDFyADjGhPlApJWtr2A7FKAzGDmzPf6v/12BNpZTs2qPeABFOJmMSRtRw5Q8h0ECMx7d4Wm1BqgzGNdgqBFwuQlxnrsBUDMJjmF4pJdvzcHMWzsP5IiR+md//V91FjbZy+xDRYaZiPWbhQxyNub0V5RhMxCG4HUl+kQfRLnpatSQY0OUJQ5wV+D0vazEurwurREiaK3p3ghPyMkIs478Tgqzq5lo9ZSTux4n4QYS7NhyaH+8Q93xUvv0TXhTzUXUEt+IMu9viapyC78Xc92Ned4QGirI03zVehI4j9jD9QzTyUmwTy+0W0bNbRGMOy+sdmf8OEyKuF0LMET263qppsGjAldjUpeN7TytuESNnmwhvS8SCYYEYkSdhgpgbhmAnPsrv5UzRcatsxmy8iQ2d9ncryr48PM7GJ7hONPZSLBbxf8tenKdVNPJwIcoG0SO7YqsYnX3BDmRiQm4Rou/cw2ZhXgZhLC7Jy0YxgS/LyxL8lu/fZS/Z1yf6rXhtH+tW2SFuvNE9vrf05Nlmu+ics3GYGO1b7IMAtTggXrP0M5sbfcL9/jXLgUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShPS01f3A8VXwoLeM7g7g56IslV8Ej2kO8OCHrFMfKWtS81v9FmW3YlrRfZIQd9yDt5J03R3cl5HR0fNUi6Xl9U7VpTGlVrt3NVE/0Sf95ECarTzfptLfCDz70SfZdkokXe7UKg3A39hcZqmj/aPewceWZaNE1mT20T67ZMi321Wmqaf0uk5JU3TH0TuLRyHz9I0nSay/AoaxzW4A4+LnLFNYpm8vGpQb05ZhnFZln2Iz/vWx4OO5/CIyJs+Pk3Ti3GPSJtFfVEux4w0Tcfioj528qAiTdNFaZrehvdEZikxTQyq2nSeU0biYZwuHhavzLJsQqeKBQ0gy7IxuFmErJlZlr2AoXi+alOsvpqQ4oVkE/IP4LOFthHjbwgAAAAASUVORK5CYII=" alt="age distribution" style="width:80px;height:25px;vertical-align:middle;" />``<br/>`top: 69:2%, 41:2%"]]
    op_10{"`<b>`Query`</b><br/>``<i>`Filter: is_primary == True`</i><br/>`➡️ df_1: 21,280×21`<br/>`⬅️ 7,034 rows × 21 cols`<br/>`↓ -14,246 (-66.9%)`<br/>`────────────────────`<br/>`🔑 patient_id: 2,189 unique`<br/>`🔑 visit_id: 2,921 unique`<br/>`🔑 department: 6 unique`<br/>`⭐ age: 78 unique`<br/>`mean=56.94 [18.0–95.0]`<br/><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGUAAAAoCAYAAADnujR9AAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjcsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvTLEjVAAAAAlwSFlzAAAMTgAADE4Bf3eMIwAABIFJREFUeJzt2luoFVUcx/GPxyNZahesCLOgmi4PBpWcsKLIDJNuVCRoWGTGbIqgeugG+VYUEdEd9lQahdVDl4d6MqL7je2lG2p5skJT85Km4iUvp4f/7DzY3uccPft0tjpfWOw9M/8185/1W+u/1sz8B3R0dChoLlr724FG0FZub8VN+KhSSpb0tz+9paW/HegtuSCv4iV831Zun9LPLvWaAftz+MoFeQWTsQAjcTheR6lSSjb2o3s1aSu3j8a8Simp2/D7rSht5faBQpAbMB/P4G/chzPxCyZWSsncTnVaMQaXYTTewKtdNVAD/R2Eh3Av7qqUkqfq2XYpSlu5vQVv5WXW/+F8T8gFeRlThCDPYnUnk+uFWDAdfwohLhUjqTNv49ZKKVnXh/6eLEbvufgZd1dKybv17LsT5TR8geH4GrdVSsn8hnr832u24EJchXWYh/mVUrIyPz4QM3EjvhEjZHWNU50qRs2x+fYu/IpFItT9imk4GyswuVJKPu6D+5mEsugM7+MDfFApJXPq1ek2fLWV20/FDFyADjGhPlApJWtr2A7FKAzGDmzPf6v/12BNpZTs2qPeABFOJmMSRtRw5Q8h0ECMx7d4Wm1BqgzGNdgqBFwuQlxnrsBUDMJjmF4pJdvzcHMWzsP5IiR+md//V91FjbZy+xDRYaZiPWbhQxyNub0V5RhMxCG4HUl+kQfRLnpatSQY0OUJQ5wV+D0vazEurwurREiaK3p3ghPyMkIs478Tgqzq5lo9ZSTux4n4QYS7NhyaH+8Q93xUvv0TXhTzUXUEt+IMu9viapyC78Xc92Ned4QGirI03zVehI4j9jD9QzTyUmwTy+0W0bNbRGMOy+sdmf8OEyKuF0LMET263qppsGjAldjUpeN7TytuESNnmwhvS8SCYYEYkSdhgpgbhmAnPsrv5UzRcatsxmy8iQ2d9ncryr48PM7GJ7hONPZSLBbxf8tenKdVNPJwIcoG0SO7YqsYnX3BDmRiQm4Rou/cw2ZhXgZhLC7Jy0YxgS/LyxL8lu/fZS/Z1yf6rXhtH+tW2SFuvNE9vrf05Nlmu+ics3GYGO1b7IMAtTggXrP0M5sbfcL9/jXLgUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShPS01f3A8VXwoLeM7g7g56IslV8Ej2kO8OCHrFMfKWtS81v9FmW3YlrRfZIQd9yDt5J03R3cl5HR0fNUi6Xl9U7VpTGlVrt3NVE/0Sf95ECarTzfptLfCDz70SfZdkokXe7UKg3A39hcZqmj/aPewceWZaNE1mT20T67ZMi321Wmqaf0uk5JU3TH0TuLRyHz9I0nSay/AoaxzW4A4+LnLFNYpm8vGpQb05ZhnFZln2Iz/vWx4OO5/CIyJs+Pk3Ti3GPSJtFfVEux4w0Tcfioj528qAiTdNFaZrehvdEZikxTQyq2nSeU0biYZwuHhavzLJsQqeKBQ0gy7IxuFmErJlZlr2AoXi+alOsvpqQ4oVkE/IP4LOFthHjbwgAAAAASUVORK5CYII=" alt="age distribution" style="width:80px;height:25px;vertical-align:middle;" />``<br/>`top: 69:2%, 85:2%"}
    op_10_removed[/"🗑️ Removed`<br/>`14,246 rows`<br/>`(66.9%)"/]
    op_11>"`<b>`Drop Duplicates`</b><br/>``<i>`Remove duplicates on patient_id, visit_date`</i><br/>`➡️ df_1: 7,034×21`<br/>`⬅️ 2,921 rows × 21 cols`<br/>`↓ -4,113 (-58.5%)`<br/>`────────────────────`<br/>`🔑 patient_id: 2,189 unique`<br/>`🔑 visit_id: 2,921 unique`<br/>`🔑 department: 6 unique`<br/>`⭐ age: 78 unique`<br/>`mean=56.75 [18.0–95.0]`<br/><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGUAAAAoCAYAAADnujR9AAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjcsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvTLEjVAAAAAlwSFlzAAAMTgAADE4Bf3eMIwAABIFJREFUeJzt2luoFVUcx/GPxyNZahesCLOgmi4PBpWcsKLIDJNuVCRoWGTGbIqgeugG+VYUEdEd9lQahdVDl4d6MqL7je2lG2p5skJT85Km4iUvp4f/7DzY3uccPft0tjpfWOw9M/8185/1W+u/1sz8B3R0dChoLlr724FG0FZub8VN+KhSSpb0tz+9paW/HegtuSCv4iV831Zun9LPLvWaAftz+MoFeQWTsQAjcTheR6lSSjb2o3s1aSu3j8a8Simp2/D7rSht5faBQpAbMB/P4G/chzPxCyZWSsncTnVaMQaXYTTewKtdNVAD/R2Eh3Av7qqUkqfq2XYpSlu5vQVv5WXW/+F8T8gFeRlThCDPYnUnk+uFWDAdfwohLhUjqTNv49ZKKVnXh/6eLEbvufgZd1dKybv17LsT5TR8geH4GrdVSsn8hnr832u24EJchXWYh/mVUrIyPz4QM3EjvhEjZHWNU50qRs2x+fYu/IpFItT9imk4GyswuVJKPu6D+5mEsugM7+MDfFApJXPq1ek2fLWV20/FDFyADjGhPlApJWtr2A7FKAzGDmzPf6v/12BNpZTs2qPeABFOJmMSRtRw5Q8h0ECMx7d4Wm1BqgzGNdgqBFwuQlxnrsBUDMJjmF4pJdvzcHMWzsP5IiR+md//V91FjbZy+xDRYaZiPWbhQxyNub0V5RhMxCG4HUl+kQfRLnpatSQY0OUJQ5wV+D0vazEurwurREiaK3p3ghPyMkIs478Tgqzq5lo9ZSTux4n4QYS7NhyaH+8Q93xUvv0TXhTzUXUEt+IMu9viapyC78Xc92Ned4QGirI03zVehI4j9jD9QzTyUmwTy+0W0bNbRGMOy+sdmf8OEyKuF0LMET263qppsGjAldjUpeN7TytuESNnmwhvS8SCYYEYkSdhgpgbhmAnPsrv5UzRcatsxmy8iQ2d9ncryr48PM7GJ7hONPZSLBbxf8tenKdVNPJwIcoG0SO7YqsYnX3BDmRiQm4Rou/cw2ZhXgZhLC7Jy0YxgS/LyxL8lu/fZS/Z1yf6rXhtH+tW2SFuvNE9vrf05Nlmu+ics3GYGO1b7IMAtTggXrP0M5sbfcL9/jXLgUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShPS01f3A8VXwoLeM7g7g56IslV8Ej2kO8OCHrFMfKWtS81v9FmW3YlrRfZIQd9yDt5J03R3cl5HR0fNUi6Xl9U7VpTGlVrt3NVE/0Sf95ECarTzfptLfCDz70SfZdkokXe7UKg3A39hcZqmj/aPewceWZaNE1mT20T67ZMi321Wmqaf0uk5JU3TH0TuLRyHz9I0nSay/AoaxzW4A4+LnLFNYpm8vGpQb05ZhnFZln2Iz/vWx4OO5/CIyJs+Pk3Ti3GPSJtFfVEux4w0Tcfioj528qAiTdNFaZrehvdEZikxTQyq2nSeU0biYZwuHhavzLJsQqeKBQ0gy7IxuFmErJlZlr2AoXi+alOsvpqQ4oVkE/IP4LOFthHjbwgAAAAASUVORK5CYII=" alt="age distribution" style="width:80px;height:25px;vertical-align:middle;" />``<br/>`top: 56:2%, 69:2%"]
    op_11_removed[/"🗑️ Removed`<br/>`4,113 rows`<br/>`(58.5%)"/]
    op_12["`<b>`Fill NA`</b><br/>``<i>`Fill NA in 3 columns`</i><br/>`➡️ df_1: 2,921×21`<br/>`⬅️ 2,921 rows × 21 cols`<br/>`────────────────────`<br/>`🔑 patient_id: 2,189 unique`<br/>`🔑 visit_id: 2,921 unique`<br/>`🔑 department: 6 unique`<br/>`⭐ age: 78 unique`<br/>`mean=56.75 [18.0–95.0]`<br/><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGUAAAAoCAYAAADnujR9AAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjcsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvTLEjVAAAAAlwSFlzAAAMTgAADE4Bf3eMIwAABIFJREFUeJzt2luoFVUcx/GPxyNZahesCLOgmi4PBpWcsKLIDJNuVCRoWGTGbIqgeugG+VYUEdEd9lQahdVDl4d6MqL7je2lG2p5skJT85Km4iUvp4f/7DzY3uccPft0tjpfWOw9M/8185/1W+u/1sz8B3R0dChoLlr724FG0FZub8VN+KhSSpb0tz+9paW/HegtuSCv4iV831Zun9LPLvWaAftz+MoFeQWTsQAjcTheR6lSSjb2o3s1aSu3j8a8Simp2/D7rSht5faBQpAbMB/P4G/chzPxCyZWSsncTnVaMQaXYTTewKtdNVAD/R2Eh3Av7qqUkqfq2XYpSlu5vQVv5WXW/+F8T8gFeRlThCDPYnUnk+uFWDAdfwohLhUjqTNv49ZKKVnXh/6eLEbvufgZd1dKybv17LsT5TR8geH4GrdVSsn8hnr832u24EJchXWYh/mVUrIyPz4QM3EjvhEjZHWNU50qRs2x+fYu/IpFItT9imk4GyswuVJKPu6D+5mEsugM7+MDfFApJXPq1ek2fLWV20/FDFyADjGhPlApJWtr2A7FKAzGDmzPf6v/12BNpZTs2qPeABFOJmMSRtRw5Q8h0ECMx7d4Wm1BqgzGNdgqBFwuQlxnrsBUDMJjmF4pJdvzcHMWzsP5IiR+md//V91FjbZy+xDRYaZiPWbhQxyNub0V5RhMxCG4HUl+kQfRLnpatSQY0OUJQ5wV+D0vazEurwurREiaK3p3ghPyMkIs478Tgqzq5lo9ZSTux4n4QYS7NhyaH+8Q93xUvv0TXhTzUXUEt+IMu9viapyC78Xc92Ned4QGirI03zVehI4j9jD9QzTyUmwTy+0W0bNbRGMOy+sdmf8OEyKuF0LMET263qppsGjAldjUpeN7TytuESNnmwhvS8SCYYEYkSdhgpgbhmAnPsrv5UzRcatsxmy8iQ2d9ncryr48PM7GJ7hONPZSLBbxf8tenKdVNPJwIcoG0SO7YqsYnX3BDmRiQm4Rou/cw2ZhXgZhLC7Jy0YxgS/LyxL8lu/fZS/Z1yf6rXhtH+tW2SFuvNE9vrf05Nlmu+ics3GYGO1b7IMAtTggXrP0M5sbfcL9/jXLgUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShPS01f3A8VXwoLeM7g7g56IslV8Ej2kO8OCHrFMfKWtS81v9FmW3YlrRfZIQd9yDt5J03R3cl5HR0fNUi6Xl9U7VpTGlVrt3NVE/0Sf95ECarTzfptLfCDz70SfZdkokXe7UKg3A39hcZqmj/aPewceWZaNE1mT20T67ZMi321Wmqaf0uk5JU3TH0TuLRyHz9I0nSay/AoaxzW4A4+LnLFNYpm8vGpQb05ZhnFZln2Iz/vWx4OO5/CIyJs+Pk3Ti3GPSJtFfVEux4w0Tcfioj528qAiTdNFaZrehvdEZikxTQyq2nSeU0biYZwuHhavzLJsQqeKBQ0gy7IxuFmErJlZlr2AoXi+alOsvpqQ4oVkE/IP4LOFthHjbwgAAAAASUVORK5CYII=" alt="age distribution" style="width:80px;height:25px;vertical-align:middle;" />``<br/>`top: 56:2%, 69:2%"]
    op_13["`<b>`Assign`</b><br/>``<i>`Create column(s): visit_month, age_group, high_...`</i><br/>`➡️ df_1: 2,921×21`<br/>`⬅️ 2,921 rows × 24 cols`<br/>`────────────────────`<br/>`🔑 patient_id: 2,189 unique`<br/>`🔑 visit_id: 2,921 unique`<br/>`🔑 department: 6 unique`<br/>`⭐ age: 78 unique`<br/>`mean=56.75 [18.0–95.0]`<br/><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGUAAAAoCAYAAADnujR9AAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjcsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvTLEjVAAAAAlwSFlzAAAMTgAADE4Bf3eMIwAABIFJREFUeJzt2luoFVUcx/GPxyNZahesCLOgmi4PBpWcsKLIDJNuVCRoWGTGbIqgeugG+VYUEdEd9lQahdVDl4d6MqL7je2lG2p5skJT85Km4iUvp4f/7DzY3uccPft0tjpfWOw9M/8185/1W+u/1sz8B3R0dChoLlr724FG0FZub8VN+KhSSpb0tz+9paW/HegtuSCv4iV831Zun9LPLvWaAftz+MoFeQWTsQAjcTheR6lSSjb2o3s1aSu3j8a8Simp2/D7rSht5faBQpAbMB/P4G/chzPxCyZWSsncTnVaMQaXYTTewKtdNVAD/R2Eh3Av7qqUkqfq2XYpSlu5vQVv5WXW/+F8T8gFeRlThCDPYnUnk+uFWDAdfwohLhUjqTNv49ZKKVnXh/6eLEbvufgZd1dKybv17LsT5TR8geH4GrdVSsn8hnr832u24EJchXWYh/mVUrIyPz4QM3EjvhEjZHWNU50qRs2x+fYu/IpFItT9imk4GyswuVJKPu6D+5mEsugM7+MDfFApJXPq1ek2fLWV20/FDFyADjGhPlApJWtr2A7FKAzGDmzPf6v/12BNpZTs2qPeABFOJmMSRtRw5Q8h0ECMx7d4Wm1BqgzGNdgqBFwuQlxnrsBUDMJjmF4pJdvzcHMWzsP5IiR+md//V91FjbZy+xDRYaZiPWbhQxyNub0V5RhMxCG4HUl+kQfRLnpatSQY0OUJQ5wV+D0vazEurwurREiaK3p3ghPyMkIs478Tgqzq5lo9ZSTux4n4QYS7NhyaH+8Q93xUvv0TXhTzUXUEt+IMu9viapyC78Xc92Ned4QGirI03zVehI4j9jD9QzTyUmwTy+0W0bNbRGMOy+sdmf8OEyKuF0LMET263qppsGjAldjUpeN7TytuESNnmwhvS8SCYYEYkSdhgpgbhmAnPsrv5UzRcatsxmy8iQ2d9ncryr48PM7GJ7hONPZSLBbxf8tenKdVNPJwIcoG0SO7YqsYnX3BDmRiQm4Rou/cw2ZhXgZhLC7Jy0YxgS/LyxL8lu/fZS/Z1yf6rXhtH+tW2SFuvNE9vrf05Nlmu+ics3GYGO1b7IMAtTggXrP0M5sbfcL9/jXLgUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShPS01f3A8VXwoLeM7g7g56IslV8Ej2kO8OCHrFMfKWtS81v9FmW3YlrRfZIQd9yDt5J03R3cl5HR0fNUi6Xl9U7VpTGlVrt3NVE/0Sf95ECarTzfptLfCDz70SfZdkokXe7UKg3A39hcZqmj/aPewceWZaNE1mT20T67ZMi321Wmqaf0uk5JU3TH0TuLRyHz9I0nSay/AoaxzW4A4+LnLFNYpm8vGpQb05ZhnFZln2Iz/vWx4OO5/CIyJs+Pk3Ti3GPSJtFfVEux4w0Tcfioj528qAiTdNFaZrehvdEZikxTQyq2nSeU0biYZwuHhavzLJsQqeKBQ0gy7IxuFmErJlZlr2AoXi+alOsvpqQ4oVkE/IP4LOFthHjbwgAAAAASUVORK5CYII=" alt="age distribution" style="width:80px;height:25px;vertical-align:middle;" />``<br/>`top: 56:2%, 69:2%"]
    op_14["`<b>`Sort`</b><br/>``<i>`Sort by visit_date, patient_id (ascending)`</i><br/>`➡️ df_1: 2,921×24`<br/>`⬅️ 2,921 rows × 24 cols`<br/>`────────────────────`<br/>`🔑 patient_id: 2,189 unique`<br/>`🔑 visit_id: 2,921 unique`<br/>`🔑 department: 6 unique`<br/>`⭐ age: 78 unique`<br/>`mean=56.75 [18.0–95.0]`<br/><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGUAAAAoCAYAAADnujR9AAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjcsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvTLEjVAAAAAlwSFlzAAAMTgAADE4Bf3eMIwAABIFJREFUeJzt2luoFVUcx/GPxyNZahesCLOgmi4PBpWcsKLIDJNuVCRoWGTGbIqgeugG+VYUEdEd9lQahdVDl4d6MqL7je2lG2p5skJT85Km4iUvp4f/7DzY3uccPft0tjpfWOw9M/8185/1W+u/1sz8B3R0dChoLlr724FG0FZub8VN+KhSSpb0tz+9paW/HegtuSCv4iV831Zun9LPLvWaAftz+MoFeQWTsQAjcTheR6lSSjb2o3s1aSu3j8a8Simp2/D7rSht5faBQpAbMB/P4G/chzPxCyZWSsncTnVaMQaXYTTewKtdNVAD/R2Eh3Av7qqUkqfq2XYpSlu5vQVv5WXW/+F8T8gFeRlThCDPYnUnk+uFWDAdfwohLhUjqTNv49ZKKVnXh/6eLEbvufgZd1dKybv17LsT5TR8geH4GrdVSsn8hnr832u24EJchXWYh/mVUrIyPz4QM3EjvhEjZHWNU50qRs2x+fYu/IpFItT9imk4GyswuVJKPu6D+5mEsugM7+MDfFApJXPq1ek2fLWV20/FDFyADjGhPlApJWtr2A7FKAzGDmzPf6v/12BNpZTs2qPeABFOJmMSRtRw5Q8h0ECMx7d4Wm1BqgzGNdgqBFwuQlxnrsBUDMJjmF4pJdvzcHMWzsP5IiR+md//V91FjbZy+xDRYaZiPWbhQxyNub0V5RhMxCG4HUl+kQfRLnpatSQY0OUJQ5wV+D0vazEurwurREiaK3p3ghPyMkIs478Tgqzq5lo9ZSTux4n4QYS7NhyaH+8Q93xUvv0TXhTzUXUEt+IMu9viapyC78Xc92Ned4QGirI03zVehI4j9jD9QzTyUmwTy+0W0bNbRGMOy+sdmf8OEyKuF0LMET263qppsGjAldjUpeN7TytuESNnmwhvS8SCYYEYkSdhgpgbhmAnPsrv5UzRcatsxmy8iQ2d9ncryr48PM7GJ7hONPZSLBbxf8tenKdVNPJwIcoG0SO7YqsYnX3BDmRiQm4Rou/cw2ZhXgZhLC7Jy0YxgS/LyxL8lu/fZS/Z1yf6rXhtH+tW2SFuvNE9vrf05Nlmu+ics3GYGO1b7IMAtTggXrP0M5sbfcL9/jXLgUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShPS01f3A8VXwoLeM7g7g56IslV8Ej2kO8OCHrFMfKWtS81v9FmW3YlrRfZIQd9yDt5J03R3cl5HR0fNUi6Xl9U7VpTGlVrt3NVE/0Sf95ECarTzfptLfCDz70SfZdkokXe7UKg3A39hcZqmj/aPewceWZaNE1mT20T67ZMi321Wmqaf0uk5JU3TH0TuLRyHz9I0nSay/AoaxzW4A4+LnLFNYpm8vGpQb05ZhnFZln2Iz/vWx4OO5/CIyJs+Pk3Ti3GPSJtFfVEux4w0Tcfioj528qAiTdNFaZrehvdEZikxTQyq2nSeU0biYZwuHhavzLJsQqeKBQ0gy7IxuFmErJlZlr2AoXi+alOsvpqQ4oVkE/IP4LOFthHjbwgAAAAASUVORK5CYII=" alt="age distribution" style="width:80px;height:25px;vertical-align:middle;" />``<br/>`top: 56:2%, 69:2%"]
    op_15>"`<b>`Drop`</b><br/>``<i>`Drop column(s): is_primary, is_abnormal`</i><br/>`➡️ df_1: 2,921×24`<br/>`⬅️ 2,921 rows × 22 cols`<br/>`────────────────────`<br/>`🔑 patient_id: 2,189 unique`<br/>`🔑 visit_id: 2,921 unique`<br/>`🔑 department: 6 unique`<br/>`⭐ age: 78 unique`<br/>`mean=56.75 [18.0–95.0]`<br/><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGUAAAAoCAYAAADnujR9AAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjcsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvTLEjVAAAAAlwSFlzAAAMTgAADE4Bf3eMIwAABIFJREFUeJzt2luoFVUcx/GPxyNZahesCLOgmi4PBpWcsKLIDJNuVCRoWGTGbIqgeugG+VYUEdEd9lQahdVDl4d6MqL7je2lG2p5skJT85Km4iUvp4f/7DzY3uccPft0tjpfWOw9M/8185/1W+u/1sz8B3R0dChoLlr724FG0FZub8VN+KhSSpb0tz+9paW/HegtuSCv4iV831Zun9LPLvWaAftz+MoFeQWTsQAjcTheR6lSSjb2o3s1aSu3j8a8Simp2/D7rSht5faBQpAbMB/P4G/chzPxCyZWSsncTnVaMQaXYTTewKtdNVAD/R2Eh3Av7qqUkqfq2XYpSlu5vQVv5WXW/+F8T8gFeRlThCDPYnUnk+uFWDAdfwohLhUjqTNv49ZKKVnXh/6eLEbvufgZd1dKybv17LsT5TR8geH4GrdVSsn8hnr832u24EJchXWYh/mVUrIyPz4QM3EjvhEjZHWNU50qRs2x+fYu/IpFItT9imk4GyswuVJKPu6D+5mEsugM7+MDfFApJXPq1ek2fLWV20/FDFyADjGhPlApJWtr2A7FKAzGDmzPf6v/12BNpZTs2qPeABFOJmMSRtRw5Q8h0ECMx7d4Wm1BqgzGNdgqBFwuQlxnrsBUDMJjmF4pJdvzcHMWzsP5IiR+md//V91FjbZy+xDRYaZiPWbhQxyNub0V5RhMxCG4HUl+kQfRLnpatSQY0OUJQ5wV+D0vazEurwurREiaK3p3ghPyMkIs478Tgqzq5lo9ZSTux4n4QYS7NhyaH+8Q93xUvv0TXhTzUXUEt+IMu9viapyC78Xc92Ned4QGirI03zVehI4j9jD9QzTyUmwTy+0W0bNbRGMOy+sdmf8OEyKuF0LMET263qppsGjAldjUpeN7TytuESNnmwhvS8SCYYEYkSdhgpgbhmAnPsrv5UzRcatsxmy8iQ2d9ncryr48PM7GJ7hONPZSLBbxf8tenKdVNPJwIcoG0SO7YqsYnX3BDmRiQm4Rou/cw2ZhXgZhLC7Jy0YxgS/LyxL8lu/fZS/Z1yf6rXhtH+tW2SFuvNE9vrf05Nlmu+ics3GYGO1b7IMAtTggXrP0M5sbfcL9/jXLgUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShNSiNKEFKI0IYUoTUghShPS01f3A8VXwoLeM7g7g56IslV8Ej2kO8OCHrFMfKWtS81v9FmW3YlrRfZIQd9yDt5J03R3cl5HR0fNUi6Xl9U7VpTGlVrt3NVE/0Sf95ECarTzfptLfCDz70SfZdkokXe7UKg3A39hcZqmj/aPewceWZaNE1mT20T67ZMi321Wmqaf0uk5JU3TH0TuLRyHz9I0nSay/AoaxzW4A4+LnLFNYpm8vGpQb05ZhnFZln2Iz/vWx4OO5/CIyJs+Pk3Ti3GPSJtFfVEux4w0Tcfioj528qAiTdNFaZrehvdEZikxTQyq2nSeU0biYZwuHhavzLJsQqeKBQ0gy7IxuFmErJlZlr2AoXi+alOsvpqQ4oVkE/IP4LOFthHjbwgAAAAASUVORK5CYII=" alt="age distribution" style="width:80px;height:25px;vertical-align:middle;" />``<br/>`top: 56:2%, 69:2%"]

    %% Connections
    op_1 --> op_2
    op_2 --> op_3
    op_3 --> op_4
    op_1 ==> op_5
    op_2 ==> op_5
    op_5 -.-> op_6
    op_6 -.-> op_6_removed
    op_6 -.-> op_7
    op_7 -.-> op_7_removed
    op_3 ==> op_8
    op_7 ==> op_8
    op_4 ==> op_9
    op_8 ==> op_9
    op_9 -.-> op_10
    op_10 -.-> op_10_removed
    op_10 -.-> op_11
    op_11 -.-> op_11_removed
    op_11 --> op_12
    op_12 --> op_13
    op_13 --> op_14
    op_14 --> op_15

    %% Styles
    style op_1 fill:#9ca3af,stroke:#6d727a,color:#000000
    style op_2 fill:#9ca3af,stroke:#6d727a,color:#000000
    style op_3 fill:#9ca3af,stroke:#6d727a,color:#000000
    style op_4 fill:#9ca3af,stroke:#6d727a,color:#000000
    style op_5 fill:#6dc993,stroke:#4c8c66,color:#000000
    style op_6 fill:#7cb3d9,stroke:#567d97,color:#000000
    style op_6_removed fill:#ffcccc,stroke:#cc0000,color:#660000,stroke-dasharray: 5 5
    style op_7 fill:#7cb3d9,stroke:#567d97,color:#000000
    style op_7_removed fill:#ffcccc,stroke:#cc0000,color:#660000,stroke-dasharray: 5 5
    style op_8 fill:#6dc993,stroke:#4c8c66,color:#000000
    style op_9 fill:#6dc993,stroke:#4c8c66,color:#000000
    style op_10 fill:#7cb3d9,stroke:#567d97,color:#000000
    style op_10_removed fill:#ffcccc,stroke:#cc0000,color:#660000,stroke-dasharray: 5 5
    style op_11 fill:#e8918a,stroke:#a26560,color:#000000
    style op_11_removed fill:#ffcccc,stroke:#cc0000,color:#660000,stroke-dasharray: 5 5
    style op_12 fill:#72d5d0,stroke:#4f9591,color:#000000
    style op_13 fill:#f0a86e,stroke:#a8754d,color:#000000
    style op_14 fill:#f5d76e,stroke:#ab964d,color:#000000
    style op_15 fill:#e8918a,stroke:#a26560,color:#000000`</div>`
        `<div class="footer">`
            Generated by pandas_flow
        `</div>`
    `</div>`
    `<script>`
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            maxTextSize: 500000,
            flowchart: {
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }
        });
    `</script>`

</body>
</html>
```

## Installation

```bash
pip install pandas-flowchart
```

Or install from source:

```bash
git clone https://github.com/yourusername/pandas-flowchart.git
cd pandas-flowchart
pip install -e .
```

## Quick Start

```python
import pandas as pd
import pandas_flow

# Setup the tracker with variables to monitor
flow = pandas_flow.setup(
    track_row_count=True,
    track_variables={
        "patient_id": "n_unique",
        "exam_date": "n_unique",
    },
    stats_variable="age",
    stats_types=["min", "max", "mean", "std", "histogram"],
)

# Your pandas operations are automatically tracked
patients = pd.read_csv("patients.csv")
exams = pd.read_csv("exams.csv")

# Merge datasets
combined = patients.merge(exams, on="patient_id", how="inner")

# Filter adults
adults = combined.query("age >= 18")

# Add calculated columns
adults = adults.assign(
    age_group=lambda x: pd.cut(x["age"], bins=[18, 30, 50, 70, 100])
)

# Remove duplicates
clean_data = adults.drop_duplicates(subset=["patient_id", "exam_date"])

# Generate the flowchart
flow.render("pipeline_flowchart.md")
```

This generates a beautiful Mermaid flowchart showing each operation with:

- Operation type and description
- Input/output row counts
- Tracked variable statistics
- Distribution histograms

## Detailed Usage

### Setting Up the Tracker

```python
import pandas_flow

flow = pandas_flow.setup(
    # Track row counts after each operation
    track_row_count=True,
  
    # Variables to monitor (name -> stat_type)
    # stat_type can be: "n_total", "n_non_null", "n_unique"
    track_variables={
        "user_id": "n_unique",
        "transaction_date": "n_unique",
        "product_category": "n_unique",
    },
  
    # Variable for detailed statistics
    stats_variable="amount",
  
    # Which stats to compute for stats_variable
    stats_types=["min", "max", "mean", "std", "top3_freq", "histogram"],
  
    # Auto-intercept pandas operations (default: True)
    auto_intercept=True,
  
    # Visual theme: "default", "dark", or "light"
    theme="default",
)
```

### Tracked Operations

The library automatically intercepts these pandas operations:

| Category                    | Operations                                                    |
| --------------------------- | ------------------------------------------------------------- |
| **Data Loading**      | `read_csv`, `read_excel`, `read_parquet`, `read_json` |
| **Filtering**         | `query`, `loc`, `iloc`, boolean indexing                |
| **Joins**             | `merge`, `join`                                           |
| **Column Operations** | `assign`, `drop`, `rename`                              |
| **Concatenation**     | `concat`                                                    |
| **Groupby**           | `groupby` + `agg`/`transform`                           |
| **Reshape**           | `pivot`, `pivot_table`, `melt`                          |
| **Cleaning**          | `drop_duplicates`, `dropna`, `fillna`                   |
| **Sorting**           | `sort_values`, `sort_index`                               |

### Manual Tracking

For operations that can't be automatically intercepted (like boolean indexing), use manual tracking:

```python
from pandas_flow.interceptors import track_filter

# Before filtering
original_df = df.copy()

# Filter with boolean indexing
df = df[df["status"] == "active"]

# Manually track the operation
track_filter(flow, original_df, df, 'status == "active"')
```

Or use the decorator pattern:

```python
@flow.track("Custom Processing", OperationType.CUSTOM)
def process_data(df):
    # Your custom logic
    return df.pipe(custom_transform)

result = process_data(input_df)
```

### Generating Output

```python
# Markdown with Mermaid code block
flow.render("pipeline.md")

# Standalone HTML page (interactive)
flow.render("pipeline.html")

# Raw Mermaid syntax
flow.render("pipeline.mmd")

# Get Mermaid code as string
mermaid_code = flow.get_mermaid(
    title="My Data Pipeline",
    direction="TB",  # TB, LR, BT, RL
    include_legend=False,
    include_stats=True,
)
```

### Context Manager Usage

```python
with pandas_flow.setup(track_variables={"id": "n_unique"}) as flow:
    df = pd.read_csv("data.csv")
    df = df.query("active == True")
    df = df.drop_duplicates()
  
    flow.render("output.md")
# Interceptors are automatically removed after the context
```

## Output Example

### Box Contents

Each operation box includes:

- **Operation name** (bold header)
- **Description** (what the operation does)
- **Input DataFrames** with source filename and dimensions
- **Output DataFrame** dimensions
- **Row change indicator** (↑ increase / ↓ decrease with percentage)
- **Tracked variable statistics**
- **Distribution histogram** (ASCII sparkline or embedded image with x-axis)

## Color Scheme

Operations are color-coded by type (pastel/less saturated colors):

| Operation Type  | Color                 |
| --------------- | --------------------- |
| Data Loading    | Soft Gray (#9ca3af)   |
| Filtering       | Soft Blue (#7cb3d9)   |
| Joins           | Soft Green (#6dc993)  |
| Column Creation | Soft Orange (#f0a86e) |
| Drop Operations | Soft Red (#e8918a)    |
| Groupby         | Soft Purple (#b99ad1) |
| Concatenation   | Soft Teal (#6bc4ce)   |
| Reshape         | Soft Pink (#f5a3c7)   |
| Sorting         | Soft Yellow (#f5d76e) |

## API Reference

### `pandas_flow.setup()`

Main entry point to create and activate a FlowTracker.

**Parameters:**

- `track_row_count` (bool): Track row counts after each operation. Default: `True`
- `track_variables` (dict): Map of variable names to stat types. Default: `None`
- `stats_variable` (str): Variable for detailed statistics. Default: `None`
- `stats_types` (list): Statistics to compute. Default: `["min", "max", "mean", "std", "top3_freq", "histogram"]`
- `auto_intercept` (bool): Auto-intercept pandas operations. Default: `True`
- `theme` (str): Color theme. Options: `"default"`, `"dark"`, `"light"`

**Returns:** `FlowTracker` instance

### `FlowTracker.render()`

Render the flowchart to a file.

**Parameters:**

- `output_path` (str): Output file path (.md, .html, or .mmd)
- `title` (str): Diagram title. Default: `"Data Flow Pipeline"`
- `direction` (str): Flow direction. Options: `"TB"`, `"LR"`, `"BT"`, `"RL"`
- `include_legend` (bool): Include color legend. Default: `False`
- `include_stats` (bool): Include statistics in boxes. Default: `True`

### `FlowTracker.get_mermaid()`

Get Mermaid code without saving to file.

### `FlowTracker.summary()`

Get a text summary of all recorded operations.

### `FlowTracker.clear()`

Clear all recorded events.

## Architecture

```
pandas_flow/
├── __init__.py          # Public API exports
├── tracker.py           # FlowTracker central class
├── events.py            # Event types and metadata classes
├── interceptors.py      # Pandas operation interceptors
├── stats.py             # Statistics calculator
├── visualization.py     # ASCII art utilities
└── mermaid_renderer.py  # Mermaid diagram generator
```

### Design Principles

1. **Non-invasive**: Intercepts operations without modifying your code
2. **Configurable**: Track only what you need
3. **Extensible**: Easy to add custom operations
4. **Performant**: Minimal overhead during data processing

## Advanced Features

### Multiple DataFrames

The library correctly handles pipelines with multiple DataFrames:

```python
df1 = pd.read_csv("sales.csv")
df2 = pd.read_csv("products.csv")
df3 = pd.read_csv("customers.csv")

# Multiple merges are tracked with proper connections
result = df1.merge(df2, on="product_id").merge(df3, on="customer_id")
```

### Chained Operations

Method chaining is fully supported:

```python
result = (
    pd.read_csv("data.csv")
    .query("status == 'active'")
    .drop_duplicates(subset=["id"])
    .assign(processed=True)
    .sort_values("date")
)
```

### Export to PNG

For PNG export, install the optional dependency:

```bash
pip install pandas-flowchart[png]
```

Then use the Mermaid CLI or a Mermaid renderer service.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

MIT License - see LICENSE file for details.
