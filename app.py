import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import altair as alt

# Set up page
st.set_page_config(
    page_title="George Vinyl Collection",
    page_icon="https://cdn-icons-png.flaticon.com/512/13/13510.png",
    layout="wide"
)

# --------------------------------------------------
# 1) Function to clean and rename the data
# --------------------------------------------------
def clean_data(df: pd.DataFrame):
    """
    Receives the raw DataFrame from Google Sheets,
    keeps only the relevant columns, renames them,
    and removes duplicates.
    """
    # Create a list to collect log messages
    log_messages = []
    
    # Log original row count
    original_count = len(df)
    log_messages.append(f"Original row count: {original_count}")
    
    # Example: columns [0..6] correspond to:
    #   a) artist, b) title, c) type, d) date, e) genre, f) country, g) link
    # Adjust these indices to match your actual sheet layout.
    df = df.iloc[:, [0, 1, 2, 3, 4, 5, 9]]
    df.columns = ["artist", "title", "type", "date", "genre", "country", "link"]
    
    # Log count after column selection
    after_columns_count = len(df)
    log_messages.append(f"Row count after column selection: {after_columns_count} (lost {original_count - after_columns_count})")
    
    # Create a copy of the dataframe before date processing
    df_with_all_dates = df.copy()
    
    # Convert 'date' column to numeric (if it's supposed to be a year)
    # Invalid values become NaN
    df["date"] = pd.to_numeric(df["date"], errors="coerce")
    
    # Count rows that would be lost due to invalid dates
    invalid_dates_count = df["date"].isna().sum()
    log_messages.append(f"Rows with invalid dates that would be dropped: {invalid_dates_count}")
    
    # Instead of dropping invalid dates, replace with a placeholder (e.g., 0)
    df["date"] = df["date"].fillna(0)
    
    # Convert the date to integer
    df["date"] = df["date"].astype(int)
    
    # Log count after date processing
    after_date_count = len(df)
    log_messages.append(f"Row count after date processing: {after_date_count} (lost {after_columns_count - after_date_count})")
    
    # Drop empty rows (all columns are NaN)
    empty_rows_before = len(df)
    df.dropna(how="all", inplace=True)
    empty_rows_after = len(df)
    log_messages.append(f"Empty rows dropped: {empty_rows_before - empty_rows_after}")
    
    # Spot duplicates
    duplicates = df[df.duplicated(keep=False)]
    duplicate_count = len(duplicates)
    log_messages.append(f"Duplicate rows found: {duplicate_count}")
    
    # Remove duplicates
    df_before_dedup = len(df)
    df.drop_duplicates(inplace=True)
    df_after_dedup = len(df)
    log_messages.append(f"Duplicates removed: {df_before_dedup - df_after_dedup}")
    
    # Final count
    log_messages.append(f"Final row count: {len(df)} (total lost: {original_count - len(df)})")
    
    return df, duplicates, log_messages

# --------------------------------------------------
# 2) Load data from Google Sheets
# --------------------------------------------------
@st.cache_data
def load_data_from_gsheets():
    # Create a connection object. (Make sure you have set up "gsheets" in .streamlit/secrets.toml)
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Read the specified worksheet
    raw_df = conn.read(
        worksheet="ΒΙΝΥΛΙΟ",
        nrows=None  # Remove or set to None to read all rows
    )
    return raw_df

# --------------------------------------------------
# 3) Main application
# --------------------------------------------------
def main():
    st.markdown("<h1 style='text-align: center; color: #CEA49C;'>The Great Vinyl Collection</h1>", 
                unsafe_allow_html=True)

    # Load data
    raw_df = load_data_from_gsheets()
    df_main, duplicates, log_messages = clean_data(raw_df)

    # Display technical information in a collapsible section
    with st.expander("Technical Information (Click to expand)", expanded=False):
        for message in log_messages:
            st.write(message)

    # Show duplicates if you want
    if not duplicates.empty:
        with st.expander("Possible duplicates found (click to expand)"):
            st.dataframe(duplicates)

    # Basic stats
    total_discs = len(df_main)

    # Sidebar info
    st.sidebar.markdown(
        f"""
        <h1 style="font-size: 40px; text-align: right; color: #E9DFCA;">
            {total_discs}
            <p style="font-size: 16px; color: #CEA49C;">discs</p>
            <p style="font-size: 14px; text-align: right; color: #CEA49C">
                <em>...and counting</em>
            </p>
        </h1>
        """,
        unsafe_allow_html=True
    )

    # Filter out rows where 'date' is 0 or missing
    df_no_zero_dates = df_main.loc[df_main["date"] != 0]

    if not df_no_zero_dates.empty:
        oldest = df_no_zero_dates.loc[df_no_zero_dates["date"].idxmin()]
        newest = df_no_zero_dates.loc[df_no_zero_dates["date"].idxmax()]
        average_release_date = int(df_no_zero_dates["date"].mean())

        st.markdown(
            f"""
            <span style='font-size:25px; color: #BEAFAF'>Newest</span> disc 
            in collection: <strong>{newest['title']}</strong> by 
            <strong>{newest['artist']}</strong>,
            <span style='font-size:20px; color: #BEAFAF'>{newest['date']}</span>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <span style='font-size:25px; color: #927676'>Oldest</span> 
            disc in collection: <strong>{oldest['title']}</strong> by 
            <strong>{oldest['artist']}</strong>, 
            <span style='font-size:20px; color: #927676'>{oldest['date']}</span>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <span style='font-size:25px; color: #EFDADA'>Average</span> release date: 
            <span style='font-size:20px; color: #EFDADA'>{average_release_date}</span>
            """,
            unsafe_allow_html=True
        )

    # Option to show the raw collection table
    if st.checkbox("Show Collection"):
        st.dataframe(df_main)

    # -------------------------------------------
    # Pie Chart: Discs by Country in selected date range
    # -------------------------------------------
    # Filter again for date != 0
    filtered_df = df_main[df_main["date"] != 0]
    if not filtered_df.empty:
        min_date_pie = int(filtered_df["date"].min())
        max_date_pie = int(filtered_df["date"].max())

        start_date_pie, end_date_pie = st.sidebar.slider(
            "Chronological range for Pie & Genre Charts:",
            min_date_pie,
            max_date_pie,
            (min_date_pie, max_date_pie)
        )

        # Filter the data based on slider
        filtered_df = df_main[df_main["date"].between(start_date_pie, end_date_pie)]

        # Prepare data for Pie Chart - Countries
        # Get counts by country
        country_counts = filtered_df["country"].value_counts()
        
        # Convert to DataFrame with clear column names
        count_countries = pd.DataFrame({
            "country": country_counts.index,
            "Discs": country_counts.values
        })

        # Optionally lump small countries into "Other"
        other_counts = 0
        threshold = 5
        countries_to_lump = []

        # Fixed: the code was using "Country" but should be "Discs" after renaming
        for idx, row in count_countries.iterrows():
            if row["Discs"] < threshold:
                other_counts += row["Discs"]
                countries_to_lump.append(row["country"])

        # Keep only big countries if you want
        if countries_to_lump:
            count_countries = count_countries[~count_countries["country"].isin(countries_to_lump)]
            # Add an "Other" row if there are any small countries
            if other_counts > 0:
                count_countries.loc[len(count_countries)] = ["Other", other_counts]

        fig_discs_per_country = px.pie(
            count_countries, 
            values="Discs", 
            names="country",
            color_discrete_sequence=px.colors.qualitative.Antique
        )
        fig_discs_per_country.update_layout(
            title=f"Discs by Country ({start_date_pie}–{end_date_pie})",
            title_x=0.45
        )
        fig_discs_per_country.update_traces(textinfo="percent+label")

        # -------------------------------------------
        # Bar Chart: Discs by Genre in selected date range
        # -------------------------------------------
        # Get Genre counts
        genre_counts = filtered_df["genre"].value_counts()
        
        # Convert to DataFrame with clear column names
        count_genres = pd.DataFrame({
            "genre": genre_counts.index,
            "Discs": genre_counts.values
        })

        # Minimum discs per genre to display
        min_val = count_genres["Discs"].min()
        max_val = count_genres["Discs"].max()
        show_min_genre = st.sidebar.number_input(
            label=f"Select minimum # of discs for each genre ({min_val} - {max_val})",
            min_value=min_val,
            max_value=max_val,
            value=min_val
        )

        # Filter out genres with fewer discs than chosen threshold
        count_genres = count_genres[count_genres["Discs"] >= show_min_genre]

        fig_discs_per_genre = px.bar(
            count_genres,
            x="genre",
            y="Discs",
            title=f"Discs by Genre ({start_date_pie}–{end_date_pie})",
            color_discrete_sequence=px.colors.qualitative.Antique,
            color="genre"
        )

        # Layout the two charts side by side
        row1_spacer1, row1_1, row1_spacer3, row1_2, row1_spacer4 = st.columns((0.1, 1.6, 0.1, 1.6, 0.1))
        with row1_1:
            st.plotly_chart(fig_discs_per_country, use_container_width=True)
        with row1_2:
            st.plotly_chart(fig_discs_per_genre, use_container_width=True)

    else:
        st.warning("No valid date values in the dataset for visualization.")

if __name__ == "__main__":
    main()